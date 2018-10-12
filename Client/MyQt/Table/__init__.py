from typing import List

from PyQt5.QtCore import pyqtSignal
from PyQt5.QtWidgets import QWidget, QHBoxLayout, QTableWidgetItem, QVBoxLayout

from Client.Configuartion.Configurable import Configurable
from Client.Configuartion.WindowConfig import Config
from Client.IProgram import IProgram
from Client.MyQt.Table.Items.LessonHeader import LessonDateItem, \
    LessonNumberItem, LessonTypeItem, LessonHeaderFactory
from Client.MyQt.Table.Items.PercentHeader import PercentHeaderItem
from Client.MyQt.Table.Items.PercentItem import PercentItem
from Client.MyQt.Table.Items.StudentHeader.StudentHeaderItem import \
    StudentHeaderItem
from Client.MyQt.Table.Items.VisitItem import VisitItem, VisitItemFactory
from Client.MyQt.Table.Section.QtMyHomeworkSection import HomeworkSection
from Client.MyQt.Table.Section.QtMyPercentSection import PercentSection
from Client.MyQt.Table.Section.QtMyVisitSection import VisitSection
from DataBase.Types import format_name
from DataBase2 import Student, Lesson


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

        self.lesson_header_factory = LessonHeaderFactory(self, program)

        self.header_height = 0
        self.first = True

        # init sections
        self.visit_table = VisitSection()
        self.percent_table = PercentSection()
        self.home_work_table = HomeworkSection()

        # share scroll menu_bar between sections
        scroll_bar = self.visit_table.verticalScrollBar()
        scroll_bar.valueChanged.connect(
            self.percent_table.verticalScrollBar().setValue)
        scroll_bar.valueChanged.connect(
            self.home_work_table.verticalScrollBar().setValue)

        # self.scroll_area.setWidget(self.visit_table)
        self.inner_layout.addWidget(self.visit_table)
        self.inner_layout.addWidget(self.percent_table)
        self.inner_layout.addWidget(self.home_work_table)

        self.students = []
        self.lessons = []

        parent.addLayout(self.inner_layout)

        self.table_item_factory = VisitItemFactory(self.program,
                                                   self.visit_table)

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

        self.percent_table.clear()
        self.percent_table.setRowCount(0)
        self.percent_table.setColumnCount(0)

        self.home_work_table.clear()
        self.home_work_table.setRowCount(0)
        self.home_work_table.setColumnCount(0)

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

        def apply_configuration():
            """
            Configure header
            """
            lesson_info = self.program.win_config["table_header"][
                'lesson_info']
            for key in lesson_info:
                row = str(key)
                visible = lesson_info[key]

                self.visit_table.setRowHidden(int(row), not visible)
                self.percent_table.setRowHidden(int(row), not visible)

        self.lessons = sorted(lessons, key=lambda x: x.date)

        self.visit_table.setColumnCount(len(lessons))

        self.visit_table.setRowCount(self.Header.COUNT)

        item1 = QTableWidgetItem()
        item1.setText("Месяц")
        self.visit_table.setVerticalHeaderItem(VisitTable.Header.MONTH, item1)

        item2 = QTableWidgetItem()
        item2.setText("День")
        self.visit_table.setVerticalHeaderItem(VisitTable.Header.DAY, item2)

        week_item = QTableWidgetItem()
        week_item.setText('Номер недели')
        self.visit_table.setVerticalHeaderItem(VisitTable.Header.WEEK_NUMBER,
                                               week_item)

        item3 = QTableWidgetItem()
        item3.setText("День недели")
        self.visit_table.setVerticalHeaderItem(VisitTable.Header.WEEKDAY,
                                               item3)

        item4 = QTableWidgetItem()
        item4.setText("Номер пары")
        self.visit_table.setVerticalHeaderItem(VisitTable.Header.LESSON, item4)

        item5 = QTableWidgetItem()
        item5.setText("Тип занятия")
        self.visit_table.setVerticalHeaderItem(VisitTable.Header.LESSONTYPE,
                                               item5)

        # percent table header
        self.percent_table.setColumnCount(1)
        # self.percent_table.resizeColumnsToContents()
        self.percent_table.setRowCount(self.Header.COUNT)
        for i in range(VisitTable.Header.COUNT):
            self.visit_table.resizeRowToContents(i)
            self.percent_table.setRowHeight(i, self.visit_table.rowHeight(i))
        self.percent_table.setSpan(0, 0, 5, 1)
        self.percent_table.setItem(0, 0, PercentHeaderItem(
            PercentItem.Orientation.ByStudents))

        self.header_height = 0

        # months = get_months(lessons)
        for column, lesson in enumerate(lessons):
            # self.visit_table.setColumnWidth(column, 15)

            header = self.lesson_header_factory.create(column, lesson)

            self.visit_table.setItem(VisitTable.Header.MONTH, column,
                                     header.month)
            self.visit_table.setItem(VisitTable.Header.DAY, column,
                                     header.month_day)
            self.visit_table.setItem(VisitTable.Header.WEEK_NUMBER, column,
                                     header.week_number)
            self.visit_table.setItem(VisitTable.Header.WEEKDAY, column,
                                     header.weekday)
            self.visit_table.setItem(VisitTable.Header.LESSON, column,
                                     header.number)
            self.visit_table.setItem(VisitTable.Header.LESSONTYPE, column,
                                     header.type)

        # week number span
        start = 0
        for column, lesson in enumerate(self.lessons):
            if self.visit_table.item(VisitTable.Header.WEEK_NUMBER,
                                     column).text() != self.visit_table.item(
                VisitTable.Header.WEEK_NUMBER, start).text():
                self.visit_table.setSpan(VisitTable.Header.WEEK_NUMBER, start,
                                         1, column - start)
                start = column
        self.visit_table.setSpan(VisitTable.Header.WEEK_NUMBER, start, 1,
                                 len(lessons) - start)

        # month Span
        start = 0
        for column, lesson in enumerate(lessons):
            if self.visit_table.item(VisitTable.Header.MONTH,
                                     column).text() != self.visit_table.item(
                VisitTable.Header.MONTH, start).text():
                self.visit_table.setSpan(VisitTable.Header.MONTH, start, 1,
                                         column - start)
                start = column
            self.visit_table.setColumnWidth(column, 20)
        self.visit_table.setSpan(VisitTable.Header.MONTH, start, 1,
                                 len(lessons) - start)

        # self.visit_table.horizontalHeader().setResizeMode(QHeaderView.ResizeToContents)

        apply_configuration()

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

        percent_item = PercentItem(self.get_row(row),
                                   PercentItem.Orientation.ByStudents)
        self.percent_table.setItem(row, 0, percent_item)

        self.visit_table.resizeRowsToContents()
        self.percent_table.resizeRowsToContents()

    def on_cellChanged(self, row, col):
        item = self.visit_table.item(row, col)

        if isinstance(item, VisitItem):
            if item.ready:
                percent_row = VisitTable.Header.COUNT + len(self.students)
                percents = [self.visit_table.item(percent_row, col),
                            self.visit_table.item(percent_row + 1, col),
                            self.percent_table.item(row, 0)]

                for percent in percents:
                    assert isinstance(percent,
                                      PercentItem), f"row:{row}, col:{col} is not PercentItem"

                    percent.refresh()

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
        self.percent_table.insertRow(index)
        # self.home_work_table.insertRow(index)

    def removeRow(self, index: int):
        """
        removes row with given index
        :param index:
        """
        self.visit_table.removeRow(index)
        self.percent_table.removeRow(index)
        # self.home_work_table.removeRow(index)

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

            self.percent_table.item(row, 0).refresh()
            self.visit_table.item(self.rowCount() - 1, col).refresh()
