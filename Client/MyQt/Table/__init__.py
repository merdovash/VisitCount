import datetime
from typing import List

from PyQt5.QtCore import pyqtSignal
from PyQt5.QtWidgets import QWidget, QHBoxLayout, QTableWidgetItem, QVBoxLayout

from Client.Configuartion.Configurable import Configurable
from Client.Configuartion.WindowConfig import Config
from Client.MyQt.Table.Items.LessonHeader import LessonDateItem, LessonNumberItem, LessonTypeItem, LessonHeaderFactory
from Client.MyQt.Table.Items.PercentHeader import PercentHeaderItem
from Client.MyQt.Table.Items.PercentItem import PercentItem
from Client.MyQt.Table.Items.StudentHeader.StudentHeaderItem import StudentHeaderItem
from Client.MyQt.Table.Items.VisitItem import VisitItem
from Client.MyQt.Table.Section.QtMyHomeworkSection import HomeworkSection
from Client.MyQt.Table.Section.QtMyPercentSection import PercentSection
from Client.MyQt.Table.Section.QtMyVisitSection import VisitSection
from Client.test import safe
from DataBase.Types import format_name


class VisitTable(QWidget, Configurable):
    show_visitation_msg = pyqtSignal(str)

    class Header(int):
        MONTH = 0
        DAY = 1
        WEEK_NUMBER = 2
        WEEKDAY = 3
        LESSON = 4
        LESSONTYPE = 5

        COUNT = 6

    @safe
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

    @safe
    def __init__(self, parent: QVBoxLayout, program):
        super().__init__()
        self.program = program
        self.db = program.db
        self._setup_config(program.win_config)
        self.inner_layout = QHBoxLayout()
        self.inner_layout.setSpacing(0)

        self.lesson_header_factory = LessonHeaderFactory(program)

        self.header_height = 0
        self.first = True

        # init sections
        self.visit_table = VisitSection()
        self.percent_table = PercentSection()
        self.home_work_table = HomeworkSection()

        # share scroll menu_bar between sections
        scroll_bar = self.visit_table.verticalScrollBar()
        scroll_bar.valueChanged.connect(self.percent_table.verticalScrollBar().setValue)
        scroll_bar.valueChanged.connect(self.home_work_table.verticalScrollBar().setValue)

        # self.scroll_area.setWidget(self.visit_table)
        self.inner_layout.addWidget(self.visit_table)
        self.inner_layout.addWidget(self.percent_table)
        self.inner_layout.addWidget(self.home_work_table)

        self.students = []
        self.lessons = []

        parent.addLayout(self.inner_layout)

        self.lessons = None

    @safe
    def _setup_config(self, window_config: Config):
        print(window_config)
        window_config.check(self)

    @safe
    def rowCount(self):
        return self.visit_table.rowCount()

    @safe
    def columnCount(self):
        return self.visit_table.columnCount()

    @safe
    def clear(self):
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

    @safe
    def show_header(self, i):
        if i == 1:
            self._show_day = not self._show_day

    @safe
    def set_horizontal_header(self, lessons: list):

        def apply_configuration():
            lesson_info = self.program.win_config["table_header"]['lesson_info']
            for key in lesson_info:
                row = str(key)
                visible = lesson_info[key]

                self.visit_table.setRowHidden(int(row), not visible)
                self.percent_table.setRowHidden(int(row), not visible)

        self.lessons = lessons
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
        self.visit_table.setVerticalHeaderItem(VisitTable.Header.WEEK_NUMBER, week_item)

        item3 = QTableWidgetItem()
        item3.setText("День недели")
        self.visit_table.setVerticalHeaderItem(VisitTable.Header.WEEKDAY, item3)

        item4 = QTableWidgetItem()
        item4.setText("Номер пары")
        self.visit_table.setVerticalHeaderItem(VisitTable.Header.LESSON, item4)

        item5 = QTableWidgetItem()
        item5.setText("Тип занятия")
        self.visit_table.setVerticalHeaderItem(VisitTable.Header.LESSONTYPE, item5)

        # percent table header
        self.percent_table.setColumnCount(1)
        # self.percent_table.resizeColumnsToContents()
        self.percent_table.setRowCount(self.Header.COUNT)
        self.percent_table.setItem(0, 0, PercentHeaderItem([], PercentItem.Orientation.ByStudents))
        self.percent_table.setSpan(0, 0, 5, 1)

        self.header_height = 0

        # months = get_months(lessons)
        for column in range(len(lessons)):
            dt = datetime.datetime.strptime(lessons[column]["date"], self.program['date_format'])

            # self.visit_table.setColumnWidth(column, 15)

            header = self.lesson_header_factory.create(lessons[column])

            self.visit_table.setItem(VisitTable.Header.MONTH, column, header.month)
            self.visit_table.setItem(VisitTable.Header.DAY, column, header.month_day)
            self.visit_table.setItem(VisitTable.Header.WEEK_NUMBER, column, header.week_number)
            self.visit_table.setItem(VisitTable.Header.WEEKDAY, column, header.weekday)
            self.visit_table.setItem(VisitTable.Header.LESSON, column, header.number)
            self.visit_table.setItem(VisitTable.Header.LESSONTYPE, column, header.type)

        # week number span
        start = 0
        for column in range(len(self.lessons)):
            if self.visit_table.item(VisitTable.Header.WEEK_NUMBER, column).text() != self.visit_table.item(
                    VisitTable.Header.WEEK_NUMBER, start).text():
                self.visit_table.setSpan(VisitTable.Header.WEEK_NUMBER, start, 1, column - start)
                start = column
        self.visit_table.setSpan(VisitTable.Header.WEEK_NUMBER, start, 1, len(lessons) - start)

        # month Span
        start = 0
        for column in range(len(lessons)):
            if self.visit_table.item(VisitTable.Header.MONTH, column).text() != self.visit_table.item(
                    VisitTable.Header.MONTH, start).text():
                self.visit_table.setSpan(VisitTable.Header.MONTH, start, 1, column - start)
                start = column
            self.visit_table.setColumnWidth(column, 20)
        self.visit_table.setSpan(VisitTable.Header.MONTH, start, 1, len(lessons) - start)

        # self.visit_table.horizontalHeader().setResizeMode(QHeaderView.ResizeToContents)

        apply_configuration()

    @safe
    def add_student(self, student: dict, visitations: list):
        self.students.append(student)
        row = self.visit_table.rowCount()
        self.insertRow(row)

        # set row header
        header_item = StudentHeaderItem(self.program, student)
        self.visit_table.setVerticalHeaderItem(row, header_item)

        completed_lessons = list(filter(lambda x: x["completed"] == 1, self.lessons))
        # print(completed_lessons)
        # fill row and find percents
        # print(student["last_name"], "visits", len(visitations))
        visitations_id = [i["lesson_id"] for i in visitations]
        for j in range(len(self.lessons)):
            if self.lessons[j] in completed_lessons:
                if self.lessons[j]["id"] in visitations_id:
                    item = VisitItem(self.visit_table, self.program, VisitItem.Status.Visited)
                else:
                    item = VisitItem(self.visit_table, self.program, VisitItem.Status.NotVisited)
            else:
                item = VisitItem(self.visit_table, self.program, VisitItem.Status.NoInfo)
            item.student = student
            item.lesson = self.lessons[j]
            self.visit_table.setItem(row, j, item)

        percent_item = PercentItem(self.get_row(row), PercentItem.Orientation.ByStudents)
        self.percent_table.setItem(row, 0, percent_item)

        header = self.percent_table.item(0, 0)
        header.percents.append(percent_item)

        self.visit_table.resizeRowsToContents()
        self.percent_table.resizeRowsToContents()

    @safe
    def fill_percents_byStudent(self):
        current_row = self.rowCount()
        self.insertRow(current_row)

        vertical_percents = []

        for col in range(self.visit_table.columnCount()):
            item = PercentItem(self.get_column(col), PercentItem.Orientation.ByLessons)
            self.visit_table.setItem(current_row, col, item)
            vertical_percents.append(item)

        self.visit_table.setVerticalHeaderItem(current_row, PercentHeaderItem(vertical_percents))

    @safe
    def insertRow(self, index: int):
        self.visit_table.insertRow(index)
        self.percent_table.insertRow(index)
        # self.home_work_table.insertRow(index)

    @safe
    def removeRow(self, index: int):
        self.visit_table.removeRow(index)
        self.percent_table.removeRow(index)
        # self.home_work_table.removeRow(index)

    @safe
    def row(self, student_id: int) -> int:
        for row in range(self.rowCount()):
            item = self.visit_table.verticalHeaderItem(row)
            if type(item) == StudentHeaderItem:
                if item.student["id"] == student_id:
                    return row
        return -1

    def get_row(self, index) -> List[VisitItem]:
        for col in range(self.colorCount()):
            item = self.visit_table.item(index, col)
            if isinstance(item, VisitItem):
                yield item

    @safe
    def col(self, lesson_id) -> int:
        for col in range(self.columnCount()):
            if self.lessons[col]["id"] == lesson_id:
                return col
        return -1

    def get_column(self, index) -> List[VisitItem]:
        for i in range(self.rowCount()):
            item = self.visit_table.item(i, index)
            if isinstance(item, VisitItem):
                yield item

    @safe
    def new_visit(self, student_id, lesson_id):
        col = self.col(lesson_id)
        row = self.row(student_id)

        item = self.visit_table.item(row, col)
        if item.status == VisitItem.Status.Visited:
            self.show_visitation_msg.emit("Студент уже отмечен")
        else:
            student = self.visit_table.verticalHeaderItem(row).student
            self.show_visitation_msg.emit(f"Студент {format_name(student)} отмечен")
            item.set_visit_status(VisitItem.Status.Visited)

            self.percent_table.item(row, 0).refresh()
            self.visit_table.item(self.rowCount() - 1, col).refresh()
