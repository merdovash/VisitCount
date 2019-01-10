from typing import List, Dict, Any

import numpy
from PyQt5.QtCore import Qt, QPoint, QRectF, pyqtSlot, QSize, QRect
from PyQt5.QtGui import QPainter, QPen, QColor, QCursor
from PyQt5.QtWidgets import QTableWidget, QAbstractItemView, QPushButton

from Client.MyQt.ColorScheme import Color
from Client.MyQt.Widgets.Table import VisitItem, HorizontalSum, VerticalSum, StudentHeaderItem
from Client.MyQt.Widgets.Table.Items import AbstractContextItem, IDraw
from Client.MyQt.Widgets.Table.Items.LessonHeader.LessonHeaderView import LessonHeaderView, LessonHeaderItem, \
    PercentHeaderItem
from Client.MyQt.Widgets.Table.Items.PercentItem import PercentItem
from Client.MyQt.Widgets.Table.Items.StudentHeader.StudentHeaderView import StudentHeaderView
from Client.MyQt.Widgets.Table.Section import Markup
from DataBase2 import Group, Student, Lesson, Discipline
from Domain import Data
from Domain.functools.Format import format_name


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
    border_pen = QPen(Color.secondary_dark)
    border_pen.setWidthF(0.5)

    textPen = QPen(Color.text_color)

    def __init__(self, program, *__args):
        super().__init__(*__args)
        self.program = program

        self.discipline = None
        self.groups = None
        self.lessons: List[Lesson] = None
        self.students = None

        self.map = VisitMap()

        self.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
        self.verticalScrollBar().valueChanged.connect(self.on_offset_changed)
        self.horizontalScrollBar().valueChanged.connect(self.on_offset_changed)

        self.setEditTriggers(QAbstractItemView.NoEditTriggers)

        self.setContextMenuPolicy(Qt.CustomContextMenu)
        self.customContextMenuRequested.connect(self.table_right_click)

        self.setVerticalHeader(StudentHeaderView(self))

        self.setHorizontalHeader(LessonHeaderView(self))
        self.horizontalHeader().setVisible(True)

        self.setCornerWidget(CornerWidget())

        self.row_hovered = -1
        self.col_hovered = -1

        self.row_height = 20
        self.col_width = 35

        self.installEventFilter(self)

        self.setMouseTracking(True)

        self.show_cross = True

        self.ready = False

        self.current_lesson = None

    @pyqtSlot(name='on_offset_changed')
    def on_offset_changed(self):
        print('offset_changed')
        Markup.setup(self)
        self.map.offset_changed(self.verticalOffset(), self.horizontalOffset())

    @pyqtSlot(name='on_table_change')
    def on_table_change(self):
        if self.lessons is not None and self.students is not None:
            Markup.setup(self)
        self.cell_changed()

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
        self.visits = numpy.array([[VisitItem(self, self.program, student, lesson)
                                    for lesson in self.lessons
                                    ] for student in self.students
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

    @pyqtSlot('PyQt_PyObject', name='set_group')
    def set_group(self, groups: List[Group]):
        """
        Устанавливает группу/группы для таблицы
        Если дисциплина установлена и список занятий не пустой, то отрисовывает таблицу

        :param groups: List[Group]
        """
        assert all([isinstance(g, Group) for g in groups])
        print('group set')

        self.groups = groups
        self.students = sorted(Student.of(groups), key=lambda student: format_name(student))

        if self.discipline is not None:
            self.find_lessons()
            if self.lessons is not None:
                self.on_ready()

    @pyqtSlot('PyQt_PyObject', name='set_discipline')
    def set_dicipline(self, discipline: Discipline):
        assert isinstance(discipline, Discipline)
        print('discipline set')

        self.discipline = discipline

        if self.groups is not None:
            self.find_lessons()
            if self.lessons is not None or len(self.lessons)>0:
                self.on_ready()

    @pyqtSlot('PyQt_PyObject', name='set_lesson')
    def set_lesson(self, lesson):
        assert isinstance(lesson, Lesson)
        print('lesson is set')

        self.current_lesson = lesson
        if self.lessons is not None and lesson in self.lessons:
            self.horizontalScrollBar().setValue(self.lessons.index(lesson))

    def end_lesson(self):
        self.current_lesson.completed = True
        self.parent().switchBtnAction()
        self.parent().setEnabledControl(True)

    def set_semester(self, semester):
        self.current_semester = semester

    def getControl(self):
        control = self.parent().getControl()
        return control

    def find_lessons(self):
        assert self.groups is not None
        assert self.discipline is not None
        assert self.current_semester is not None

        self.lessons = Data.lessons_of(
            professor=self.program.professor,
            discipline=self.discipline,
            groups=self.groups,
            semester=self.current_semester
        )

    def resizeEvent(self, QResizeEvent):
        super().resizeEvent(QResizeEvent)
        self.on_table_change()
        self.map.offset_changed(self.verticalOffset(), self.horizontalOffset())

    def table_right_click(self, event: QPoint):
        """
        Slot
        Shows context menu of item under mouse pointer if item is AbstractContextItem
        :param event:
        """
        index = self.indexAt(event)
        row, col = index.row(), index.column()
        item = self.item(row, col)

        if isinstance(item, AbstractContextItem):
            real_pos = QCursor.pos()
            item.show_context_menu(real_pos)

    def mouseMoveEvent(self, event):
        try:
            item, row, col = self.find_item(event.pos())
            self.set_hover(row, col)
        except IndexError:
            self.set_hover(-1, -1)
        except TypeError:
            pass

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
                        item.draw(p, rect, self.isHighlighted(row, col), self.isCurrentLesson(item.lesson))
                    elif isinstance(item, HorizontalSum):
                        rect = self.map[row, col].rect
                        item.draw(p, rect, self.isHighlighted(row, col))
                    elif isinstance(item, VerticalSum):
                        rect = self.map[row, col].rect
                        item.draw(p, rect, self.isHighlighted(row, col))
                else:
                    pass

                current_point.setX(current_point.x() + width)

            current_point.setX(-1)
            current_point.setY(current_point.y() + height)

            if current_abs_row:
                abs_row = False

        # # рисуем ячейки для занятий
        # for col, l in enumerate(self.parent().lessons):
        #     width = self.columnWidth(col)
        #     # рисуем ячейки посещений
        #     for row, st in enumerate(self.parent().students):
        #         height = self.rowHeight(row)
        #         item = self.item(row, col)
        #         if isinstance(item, IDraw):
        #             rect = QRectF(started_point[0], started_point[1], width, height)
        #             item.draw(p, rect, self.isHighlighted(row, col))
        #
        #         started_point[1] += height
        #
        #     # рисуем ячейки процентов по занятиям
        #     for percent_row in range(2):
        #         row = len(self.parent().students) + percent_row
        #
        #         y_pos = self.height() - self.horizontalHeader().height() - self.rowHeight(row) * (
        #                     2 - percent_row) + self.verticalOffset() - self.horizontalScrollBar().height()
        #
        #         item = self.item(row, col)
        #         if isinstance(item, PercentItem):
        #             item.refresh()
        #         self.draw_item(p, item, row, col, [started_point[0], y_pos])
        #         started_point[1] += self.rowHeight(row)
        #     else:
        #         started_point[1] = -1
        #
        #     started_point[0] += width
        #
        # # рисуем ячейки для процентов по студентам
        # for col in range(len(self.parent().lessons), len(self.parent().lessons)+2):
        #     for row in range(len(self.parent().students)):
        #         pass

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

        p.setPen(self.textPen)
        p.drawText(rect, Qt.AlignCenter, item.text())

        p.setPen(self.border_pen)
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

    def isHighlighted(self, row, col):
        return row == self.row_hovered or col == self.col_hovered

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

    def set_hover(self, row, col):
        if self.row_hovered != row \
                or self.col_hovered != col \
                or (row == -1 and self.row_hovered != -1) \
                or (col == -1 and self.col_hovered != -1):
            self.col_hovered = col

            self.verticalHeader().set_row_hovered(row)
            self.horizontalHeader().set_hovered(col)

            self.model().dataChanged.emit(self.model().index(0, 0),
                                          self.model().index(self.columnCount() - 1, self.rowCount() - 1))

            self.viewport().repaint()

    def set_row_hovered(self, row):
        self.row_hovered = row
        self.model().dataChanged.emit(self.model().index(0, 0),
                                      self.model().index(self.columnCount() - 1, self.rowCount() - 1))
        self.viewport().repaint()

    def set_row_hover(self, row):
        self.set_hover(row, self.col_hovered)

    def set_col_hover(self, col):
        self.set_hover(self.row_hovered, col)

    def select_current_lesson(self, lesson):
        self.parent().set_current_lesson(lesson)

    def switch_show_table_cross(self):
        self.show_cross = not self.show_cross

    # def eventFilter(self, obj, event):
    #    if event.type() != QtCore.QEvent.Paint or not isinstance(obj, QtWidgets.QAbstractButton):
    #        return False

#
#    # Paint by hand (borrowed from QTableCornerButton)
#    opt = QtWidgets.QStyleOptionHeader()
#    opt.initFrom(obj)
#    styleState = QtWidgets.QStyle.State_None
#    if obj.isEnabled():
#        styleState |= QtWidgets.QStyle.State_Enabled
#    if obj.isActiveWindow():
#        styleState |= QtWidgets.QStyle.State_Active
#    if obj.isDown():
#        styleState |= QtWidgets.QStyle.State_Sunken
#    opt.state = styleState
#    opt.rect = obj.rect()
#    # This line is the only difference to QTableCornerButton
#    opt.text = obj.text()
#    opt.position = QtWidgets.QStyleOptionHeader.OnlyOneSection
#    painter = QtWidgets.QStylePainter(obj)
#    painter.drawControl(QtWidgets.QStyle.CE_Header, opt)
#
#    return True
#
