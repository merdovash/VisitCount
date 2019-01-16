from typing import List, Dict, Any

import numpy
from PyQt5.QtCore import Qt, QPoint, QRectF, pyqtSlot, QSize, QRect, pyqtSignal
from PyQt5.QtGui import QPainter, QPen, QColor, QCursor
from PyQt5.QtWidgets import QTableWidget, QAbstractItemView, QPushButton, QMenu

from Client.IProgram import IProgram
from Client.MyQt.ColorScheme import Color
from Client.MyQt.Widgets.Table.Items import IDraw
from Client.MyQt.Widgets.Table.Items.LessonHeader.LessonHeaderView import LessonHeaderView, LessonHeaderItem, \
    PercentHeaderItem
from Client.MyQt.Widgets.Table.Items.PercentItem import PercentItem, HorizontalSum, VerticalSum
from Client.MyQt.Widgets.Table.Items.StudentHeader.StudentHeaderItem import StudentHeaderItem
from Client.MyQt.Widgets.Table.Items.StudentHeader.StudentHeaderView import StudentHeaderView
from Client.MyQt.Widgets.Table.Items.VisitItem import VisitItem
from Client.MyQt.Widgets.Table.Section import Markup
from Client.Reader.Functor.NewVisit import NewVisitOnRead
from DataBase2 import Group, Student, Lesson, Discipline, Professor
from Domain import Data


class CornerWidget(QPushButton):
    def __init__(self, *args):
        super().__init__(*args)

        self.setStyleSheet("CornerWidget{ background-color:#ededed}")

    def paintEvent(self, QPaintEvent):
        p = QPainter(self)

        rect = QRectF(0, 0, self.width(), self.height())

        p.fillRect(rect, Color.secondary)
        p.drawRect(rect)
        p.drawLine(0, 0, self.width(), self.height())


class Column:
    index: int
    header: StudentHeaderItem
    items: List[VisitItem]
    visit_count: PercentItem
    visit_rate: PercentItem

    def __init__(self, index, header):
        self.index = index
        self.header = header

    def set_visits(self, visit_items: List[VisitItem]):
        assert all([isinstance(vi, VisitItem) for vi in visit_items])

        self.items = visit_items
        self.visit_count = VerticalSum(self.items, absolute=True)
        self.visit_rate = VerticalSum(self.items, absolute=False)


class Row:
    index: int
    header: StudentHeaderItem
    items: List[VisitItem]
    visit_count: PercentItem
    visit_rate: PercentItem

    def __init__(self, index, header):
        self.index = index
        self.header = header
        self.items = []

    def set_visits(self, visit_items: List[VisitItem]):
        assert all([isinstance(vi, VisitItem) for vi in visit_items])

        self.items = visit_items
        self.visit_count = HorizontalSum(visit_items, absolute=True)
        self.visit_rate = HorizontalSum(visit_items, absolute=False)


class DrawInfo:
    _point: QPoint
    point: QPoint
    size = QSize
    rect = QRect

    def __init__(self, x, y, width, height, frozen_x=False, frozen_y=False):
        self._point = QPoint(x, y)
        self.size = QSize(width, height)
        self.point = self._point
        self.frozen_x = frozen_x
        self.frozen_y = frozen_y
        self.setup()

    def offset_changed(self, vertical_offset, horizontal_offset):
        self.point = self._point - QPoint(
            0 if self.frozen_x else horizontal_offset,
            0 if self.frozen_y else vertical_offset)
        self.setup()

    def setup(self):
        self.rect = QRect(self.point, self.size)


class VisitMap:
    def __init__(self):
        self.items: Dict[Any, DrawInfo] = {}

    def offset_changed(self, vertical_offset, horizontal_offset):
        for item in self.items.values():
            item.offset_changed(vertical_offset, horizontal_offset)

    def __getitem__(self, item):
        try:
            return self.items[item]
        except KeyError:
            return None

    def __setitem__(self, key, value):
        self.items[key] = value


class VisitSection(QTableWidget):
    DEFAULT_BORDER_PEN = QPen(Color.secondary_dark)
    DEFAULT_BORDER_PEN.setWidthF(0.5)
    DEFAULT_TEXT_PEN = QPen(Color.text_color)

    visitations_changed = pyqtSignal(int, int)

    current_semester: int = None
    current_lesson: Lesson = None
    discipline: Discipline = None
    groups: List[Group] = None
    lessons: List[Lesson] = None
    students: List[Student] = None

    ready = False
    in_progress = False

    professor: Professor = None

    def __init__(self, selector, *__args):
        super().__init__(*__args)
        self.setParent(selector)

        self.program: IProgram = selector.program

        self.map = VisitMap()

        self.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
        self.setVerticalScrollMode(QAbstractItemView.ScrollPerPixel)

        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
        self.setHorizontalScrollMode(QAbstractItemView.ScrollPerPixel)

        self.setEditTriggers(QAbstractItemView.NoEditTriggers)

        self.setContextMenuPolicy(Qt.CustomContextMenu)

        self.setVerticalHeader(StudentHeaderView(self))

        self.setHorizontalHeader(LessonHeaderView(self))
        self.horizontalHeader().setVisible(True)

        self.setCornerWidget(CornerWidget())

        self.row_height = 20
        self.col_width = 35

        self.installEventFilter(self)

        self.customContextMenuRequested.connect(self.on_table_right_click)

        self.verticalScrollBar().valueChanged.connect(self.on_offset_changed)
        self.verticalScrollBar().valueChanged.connect(self.verticalHeader().setOffset)

        self.horizontalScrollBar().valueChanged.connect(self.on_offset_changed)
        self.horizontalScrollBar().valueChanged.connect(self.horizontalHeader().setOffset)

        self.itemChanged.connect(print)

    @pyqtSlot('PyQt_PyObject', 'PyQt_PyObject', name='update_data')
    def update_data(self, lessons, group):
        self.lessons = lessons
        self.students = Student.of(group)

        self.horizontalHeader().set_lessons(self.lessons)
        self.verticalHeader().set_students(self.students)

        self.on_ready()

    @pyqtSlot('PyQt_PyObject', 'PyQt_PyObject', name='set_lesson')
    def on_lesson_change(self, lessons, current_lesson):
        assert isinstance(current_lesson, Lesson)
        print('lesson is set')

        self.current_lesson = current_lesson
        if self.lessons is not None and current_lesson in self.lessons:
            self.horizontalScrollBar().setValue(self.lessons.index(current_lesson)*self.columnWidth(0))

    @pyqtSlot('PyQt_PyObject', name='on_lesson_start')
    def on_lesson_start(self, lesson):
        assert self.current_lesson == lesson
        self.in_progress = True
        self.program.reader().on_read(NewVisitOnRead(lesson))

    @pyqtSlot(name='on_lesson_stop')
    def on_lesson_stop(self):
        self.in_progress = False
        self.current_lesson.completed = True

    @pyqtSlot(name='on_offset_changed')
    def on_offset_changed(self):
        Markup.setup(self)
        self.map.offset_changed(self.verticalOffset(), self.horizontalOffset())

    @pyqtSlot(name='on_ready')
    def on_ready(self):
        self.ready = True
        Markup.setup(self)
        self.map = VisitMap()
        self.map.offset_changed(self.verticalOffset(), self.horizontalOffset())
        self.clear()

        self.students_header = {}
        self.lessons_header = {}

        self.setRowCount(len(self.students) + 2)
        self.setColumnCount(len(self.lessons) + 2)

        # init rows and columns
        for row, student in enumerate(self.students):
            header_item = StudentHeaderItem(self.program, student)
            self.students_header[student] = Row(row, header_item)

            for col, lesson in enumerate(self.lessons):
                lesson_header_item = LessonHeaderItem(lesson, self.program)
                self.lessons_header[lesson] = Column(col, lesson_header_item)

        # init visit items
        self.visits = numpy.array([[VisitItem(self.program, student, lesson)
                                    for col, lesson in enumerate(self.lessons)
                                    ] for row, student in enumerate(self.students)
                                   ])

        # set visit items to rows
        for row, student in enumerate(self.students):
            self.students_header[student].set_visits(self.visits[row, :])

        # set visit items in columns
        for col, lesson in enumerate(self.lessons):
            self.lessons_header[lesson].set_visits(self.visits[:, col])

        self._fillVerticalHeader()
        self._fillHorizontalHeader()
        self._fillVisitSection()
        self._fillVerticalPercent()
        self._fillHorizontalPercent()

        self.cell_changed()

    def _fillHorizontalPercent(self):
        for col_index, lesson in enumerate(self.lessons_header.keys()):
            column = self.lessons_header[lesson]

            self.setItem(
                Markup.visit_count_row_index,
                col_index,
                column.visit_count
            )

            self.setItem(
                Markup.visit_rate_row_index,
                col_index,
                column.visit_rate
            )

    def _fillVerticalPercent(self):
        for row_index, student in enumerate(self.students_header.keys()):
            row = self.students_header[student]

            self.setItem(
                row_index,
                Markup.visit_rate_col_index,
                row.visit_rate
            )

            self.setItem(
                row_index,
                Markup.visit_count_col_index,
                row.visit_count
            )

    def _fillVisitSection(self):
        for row in range(len(self.students)):
            for col in range(len(self.lessons)):
                self.setItem(row, col, self.visits[row, col])

    def _fillVerticalHeader(self):
        for row, student in enumerate(self.students):
            self.setVerticalHeaderItem(row, self.students_header[student].header)
            self.setRowHeight(row, 20)

        self.setVerticalHeaderItem(
            Markup.visit_count_row_index,
            PercentHeaderItem(orientation=Qt.Horizontal, absolute=True))
        self.setRowHeight(Markup.visit_count_row_index, 25)

        self.setVerticalHeaderItem(
            Markup.visit_rate_row_index,
            PercentHeaderItem(orientation=Qt.Horizontal, absolute=False))
        self.setRowHeight(Markup.visit_rate_row_index, 25)

    def _fillHorizontalHeader(self):
        for col, lesson in enumerate(self.lessons):
            self.setHorizontalHeaderItem(col, self.lessons_header[lesson].header)
            self.setColumnWidth(col, 35)

        self.setHorizontalHeaderItem(
            Markup.visit_count_col_index,
            PercentHeaderItem(orientation=Qt.Vertical, absolute=True))
        self.setColumnWidth(Markup.visit_count_col_index, 45)

        self.setHorizontalHeaderItem(
            Markup.visit_rate_col_index,
            PercentHeaderItem(orientation=Qt.Vertical, absolute=False))
        self.setColumnWidth(Markup.visit_rate_col_index, 45)

    def end_lesson(self):
        self.current_lesson.completed = True
        self.parent().switchBtnAction()
        self.parent().setEnabledControl(True)

        self.professor.session.commit()

    def find_lessons(self):
        if self.groups is not None:
            if self.discipline is not None:
                if self.current_semester is not None:
                    self.lessons = Data.lessons_of(
                        professor=self.program.professor,
                        discipline=self.discipline,
                        groups=self.groups,
                        semester=self.current_semester
                    )
                else:
                    print('no semester')
            else:
                print('no discipline')
        else:
            print('no group')

    def resizeEvent(self, QResizeEvent):
        super().resizeEvent(QResizeEvent)
        Markup.setup(self)
        self.map.offset_changed(self.verticalOffset(), self.horizontalOffset())

    @pyqtSlot(QPoint, name='on_table_right_click')
    def on_table_right_click(self, event: QPoint):
        """
        Slot
        Shows context menu of item under mouse pointer if item is AbstractContextItem
        :param event:
        """
        index = self.indexAt(event)
        row, col = index.row(), index.column()
        item: VisitItem = self.item(row, col)

        menu = QMenu()

        if self.lessons[col].completed:
            menu.addSection('Изменить данные')

            if item.isVisit():
                menu.addAction('Исключить посещение', item.del_visit_by_professor)
            else:
                menu.addAction('Отметить посещение', item.set_visited_by_professor)
        else:
            menu.addSection('пусто')

        menu.exec_(QCursor().pos())

    def paintEvent(self, QPaintEvent):
        if not self.ready:
            return
        Markup.setup(self)
        p = QPainter(self.viewport())

        self.horizontalHeader().update()

        offset_point = QPoint(self.horizontalOffset(), self.verticalOffset())
        current_point = QPoint(-1, -1)

        current_abs_row = False

        for row in range(len(self.students) + 2):
            height = self.rowHeight(row)

            for col in range(self.columnCount()):
                width = self.columnWidth(col)
                item = self.item(row, col)
                if self.map[row, col] is None:
                    if isinstance(item, VisitItem):
                        self.map[row, col] = DrawInfo(
                            current_point.x(),
                            current_point.y(),
                            width,
                            height)
                    elif isinstance(item, VerticalSum):
                        self.map[row, col] = DrawInfo(
                            current_point.x(),
                            Markup.visit_count_row if item.absolute else Markup.visit_rate_row,
                            width,
                            height,
                            frozen_y=True)
                    elif isinstance(item, HorizontalSum):
                        self.map[row, col] = DrawInfo(
                            Markup.visit_count_col if item.absolute else Markup.visit_rate_col,
                            current_point.y(),
                            width,
                            height,
                            frozen_x=True)

                if isinstance(item, IDraw):
                    if isinstance(item, VisitItem):
                        rect = self.map[row, col].rect
                        item.draw(p, rect, False, self.isCurrentLesson(item.lesson))
                    elif isinstance(item, HorizontalSum):
                        rect = self.map[row, col].rect
                        item.draw(p, rect, False)
                    elif isinstance(item, VerticalSum):
                        rect = self.map[row, col].rect
                        item.draw(p, rect, False)
                else:
                    pass

                current_point.setX(current_point.x() + width)

            current_point.setX(-1)
            current_point.setY(current_point.y() + height)

            if current_abs_row:
                abs_row = False

    def isCurrentLesson(self, lesson):
        if self.current_lesson:
            return self.current_lesson == lesson
        return False

    def cell_changed(self):
        self.model().dataChanged.emit(self.model().index(0, 0),
                                      self.model().index(self.columnCount() - 1, self.rowCount() - 1))

        self.viewport().update()

    def force_repaint(self):
        self.model().dataChanged.emit(self.model().index(0, 0),
                                      self.model().index(self.columnCount() - 1, self.rowCount() - 1))

        self.viewport().repaint()

    def draw_item(self, p: QPainter, item: VisitItem or PercentItem, row, col, started_point):
        width = self.columnWidth(col)
        height = self.rowHeight(row)

        rect = QRectF(started_point[0] - self.horizontalOffset(), started_point[1] - self.verticalOffset(),
                      width, height)

        p.fillRect(rect, self.get_color(item, row, col))

        p.setPen(self.DEFAULT_TEXT_PEN)
        p.drawText(rect, Qt.AlignCenter, item.text())

        p.setPen(self.DEFAULT_BORDER_PEN)
        p.drawRect(rect)

    def get_color(self, item, row, col):
        if isinstance(item, VisitItem):
            if self.show_cross and (row == self.row_hovered or col == self.col_hovered):
                return Color.to_accent(QColor(item.get_color()))
            else:
                return QColor(item.get_color())
        else:
            if self.show_cross and (row == self.row_hovered or col == self.col_hovered):
                return Color.secondary_light_accent
            else:
                return Color.secondary_light

    def find_item(self, pos: QPoint):
        def find_row(target_y):
            if target_y > Markup.visit_rate_row:
                return Markup.visit_rate_row_index
            elif target_y > Markup.visit_count_col:
                return Markup.visit_count_row_index
            else:
                current_y = - self.verticalOffset()

                for row in range(self.rowCount()):
                    height = self.rowHeight(row)
                    if current_y <= target_y <= current_y + height:
                        return row

                    current_y += height
                else:
                    return -1

        def find_col(target_x):
            if target_x > Markup.visit_rate_col:
                return Markup.visit_rate_col_index
            elif target_x > Markup.visit_count_col:
                return Markup.visit_count_col_index
            else:
                current_x = - self.horizontalOffset()

                for col in range(self.columnCount()):
                    width = self.columnWidth(col)
                    if current_x <= target_x <= current_x + width:
                        return col
                    current_x += width
                else:
                    return -1

        if not self.ready:
            return
        row, col = find_row(pos.y()), find_col(pos.x())
        return self.item(row, col), row, col

    def horizontalHeader(self)-> LessonHeaderView:
        return super().horizontalHeader()
