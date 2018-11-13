from typing import List

from PyQt5.QtCore import pyqtSignal, Qt
from PyQt5.QtGui import QDropEvent
from PyQt5.QtWidgets import QWidget, QHBoxLayout, QVBoxLayout

from Client.Configuartion.Configurable import Configurable
from Client.Configuartion.WindowConfig import Config
from Client.IProgram import IProgram
from Client.MyQt.Table.Items.LessonHeader.LessonHeaderView import LessonHeaderItem
from Client.MyQt.Table.Items.PercentHeader import PercentHeaderItem
from Client.MyQt.Table.Items.PercentItem import PercentItem
from Client.MyQt.Table.Items.StudentHeader.StudentHeaderItem import \
    StudentHeaderItem
from Client.MyQt.Table.Items.StudentHeader.StudentHeaderView import \
    StudentHeaderView
from Client.MyQt.Table.Items.VisitItem import VisitItem, VisitItemFactory
from Client.MyQt.Table.Section.QtMyHomeworkSection import HomeworkSection
from Client.MyQt.Table.Section.QtMyPercentSection import PercentSection
from Client.MyQt.Table.Section.QtMyVisitSection import VisitSection
from DataBase2 import Student, Lesson
from DataBase2.Types import format_name


class VisitTable(QWidget, Configurable):
    show_visitation_msg = pyqtSignal(str, bool)

    class Header(int):
        MONTH = 0
        DAY = 1
        WEEK_NUMBER = 2
        WEEKDAY = 3
        LESSON = 4
        LESSONTYPE = 5

        COUNT = 6

    def __default__(self):
        return {
            "table_header": {
                "lesson_info": {
                    str(VisitTable.Header.MONTH): True,
                    str(VisitTable.Header.LESSON): True,
                    str(VisitTable.Header.WEEK_NUMBER): True,
                    str(VisitTable.Header.WEEKDAY): False,
                    str(VisitTable.Header.DAY): True,
                    str(VisitTable.Header.LESSONTYPE): True
                }
            }
        }

    def __init__(self, parent: QVBoxLayout, program: IProgram):
        super().__init__()
        self.program: IProgram = program
        self._setup_config(program.win_config)
        self.inner_layout = QHBoxLayout()
        self.inner_layout.setSpacing(0)

        self.header_height = 0
        self.first = True

        # init sections
        self.visit_table = VisitSection(self)

        # share scroll menu_bar between sections
        scroll_bar = self.visit_table.verticalScrollBar()

        # self.scroll_area.setWidget(self.visit_table)
        self.inner_layout.addWidget(self.visit_table)

        self.students = []
        self.lessons = []

        parent.addLayout(self.inner_layout)

        self.table_item_factory = VisitItemFactory(self.program,
                                                   self.visit_table)

        self.setAcceptDrops(True)
        # self.setDefaultDropAction(Qt.MoveAction)
        # self.setDragDropMode(QtGui.QAbstractItemView.DragDrop)

    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls:
            event.accept()
        else:
            event.ignore()

    def dragMoveEvent(self, event):
        if event.mimeData().hasUrls:
            event.setDropAction(Qt.CopyAction)
            event.accept()
        else:
            event.ignore()

    def dropEvent(self, event: QDropEvent):
        print(event)
        if event.mimeData().hasUrls:
            event.setDropAction(Qt.CopyAction)
            event.accept()

            self.program.window.excel_reader.read(event.mimeData().urls()[0])
        else:
            event.ignore()

    def _setup_config(self, window_config: Config):
        print(window_config)
        window_config.check(self)

    def rowCount(self):
        """
        Returns count of rows
        :return: Int
        """
        return self.visit_table.rowCount()

    def column_count(self):
        """
        Returns count of columns of visit table
        :return: Int
        """
        return self.visit_table.columnCount()

    def clear(self):
        """
        Clears table
        """
        try:
            self.visit_table.cellChanged.disconnect()
        except TypeError:
            pass

        self.visit_table.clear()
        self.visit_table.setRowCount(0)
        self.visit_table.setColumnCount(0)

        self.students = []
        self.lessons = []

    def show_header(self, i):
        """
        switch header row status
        :param i:
        """
        if i == 1:
            self._show_day = not self._show_day

    def set_horizontal_header(self, lessons: List[Lesson]):
        """
        Fill horizontal header with given Lessons

        :param lessons: List of Lesson
        """

        self.lessons = sorted(lessons, key=lambda x: x.date)

        self.visit_table.setColumnCount(len(lessons))

        for col, lesson in enumerate(self.lessons):
            self.visit_table.setHorizontalHeaderItem(col, LessonHeaderItem(lesson, self.program))
            self.visit_table.setColumnWidth(col, 15)

    def add_student(self, student: Student):
        """
        add student and his visitations
        :param student: Student
        """
        self.students.append(student)
        row = self.visit_table.rowCount()
        self.insertRow(row)

        # set row header
        header_item = StudentHeaderItem(self.program, student)
        self.visit_table.setVerticalHeaderItem(row, header_item)

        for lesson_index, lesson in enumerate(self.lessons):
            item = self.table_item_factory.create(student, lesson)

            self.visit_table.setItem(row, lesson_index, item)

        self.visit_table.resizeRowToContents(row)

        percent_item = PercentItem(self.get_row(row),
                                   PercentItem.Orientation.ByStudents)
        # TODO percent item

    def on_cellChanged(self, row, col):
        item = self.visit_table.item(row, col)

        if isinstance(item, VisitItem):
            if item.ready:
                percent_row = VisitTable.Header.COUNT + len(self.students)
                percents = [self.visit_table.item(percent_row, col),
                            self.visit_table.item(percent_row + 1, col)]

                for percent in percents:
                    # assert isinstance(percent,
                    #                   PercentItem), f"row:{row}, col:{col} is not PercentItem, percent is {type(
                    # percent)}"

                    # percent.refresh()
                    pass

    def fill_percents_byStudent(self):
        """
        fill percents
        """
        student_count = self.rowCount() - self.Header.COUNT

        absolute_percent_row_index = self.rowCount()
        self.insertRow(absolute_percent_row_index)

        rel_percent_row_index = self.rowCount()
        self.insertRow(rel_percent_row_index)

        vertical_percents = []

        for col in range(self.visit_table.columnCount()):
            item = PercentItem(self.get_column(col),
                               PercentItem.Orientation.ByLessons, True)
            self.visit_table.setItem(absolute_percent_row_index, col, item)
            vertical_percents.append(item)

            item = PercentItem(self.get_column(col),
                               PercentItem.Orientation.ByLessons)
            self.visit_table.setItem(rel_percent_row_index, col, item)
            vertical_percents.append(item)

        self.visit_table.setVerticalHeaderItem(absolute_percent_row_index,
                                               PercentHeaderItem(student_count,
                                                                 absolute=True))
        self.visit_table.setVerticalHeaderItem(rel_percent_row_index,
                                               PercentHeaderItem(
                                                   student_count))

        self.visit_table.cellChanged.connect(self.on_cellChanged)

    def insertRow(self, index: int):
        """
        inserts row on given index
        :param index:
        """
        self.visit_table.insertRow(index)

    def removeRow(self, index: int):
        """
        removes row with given index
        :param index:
        """
        self.visit_table.removeRow(index)

    def row(self, student: Student) -> int:
        """
        row index of Student

        :param student: Student
        :return: int
        """
        for row in range(self.rowCount()):
            item = self.visit_table.verticalHeaderItem(row)
            if type(item) == StudentHeaderItem:
                if item.student == student:
                    return row
        return -1

    def get_row(self, index) -> List[VisitItem]:
        """
        returns all VisitItem from row
        :param index: index of row
        """

        def generator_():
            for col in range(self.colorCount()):
                item = self.visit_table.item(index, col)
                if isinstance(item, VisitItem):
                    yield item

        return list(generator_())

    def col(self, lesson: Lesson) -> int:
        """
        Returns table column index of Lesson

        :param lesson: Lesson
        :return: column index
        """
        for col in range(self.column_count()):
            if self.lessons[col] == lesson:
                return col
        return -1

    def get_column(self, index) -> List[VisitItem]:
        """
        returns all VisitItem of column
        :param index: index of column
        """
        assert 0 <= index < self.visit_table.columnCount(), f"index={index} is out range"

        def _generator():
            for i in range(self.rowCount()):
                item = self.visit_table.item(i, index)
                if isinstance(item, VisitItem):
                    yield item

        return list(_generator())

    def new_visit(self, student: Student, lesson: Lesson):
        """
        Update VisitItem for Student-Lesson

        :param student: Student
        :param lesson: Lesson
        """
        col = self.col(lesson)
        row = self.row(student)

        item = self.visit_table.item(row, col)
        if item.status == VisitItem.Status.Visited:
            self.show_visitation_msg.emit("Студент уже отмечен")
        else:
            self.show_visitation_msg.emit(
                f"Студент {format_name(student)} отмечен")

            self.visit_table.item(self.rowCount() - 1, col).refresh()

    def set_current_lesson(self, lesson):
        self.parent().set_current_lesson(lesson)

    def switch_show_table_cross(self):
        self.visit_table.switch_show_table_cross()
