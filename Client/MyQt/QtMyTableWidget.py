import datetime
import traceback

from PyQt5.QtWidgets import QWidget, QHBoxLayout, QTableWidgetItem, QVBoxLayout, QMainWindow

from Client.Configuartion import WindowConfig
from Client.Configuartion.Configurable import Configurable
from Client.Configuartion.WindowConfig import Config
from Client.MyQt.QtMyStatusBar import QStatusMessage
from Client.MyQt.QtMyWidgetItem import VisitItem, LessonTypeItem, MonthTableItem, \
    StudentHeaderItem, \
    PercentItem, PercentHeaderItem, LessonDateItem, LessonNumberItem, WeekDayItem
from Client.MyQt.Section.QtMyHomeworkSection import HomeworkSection
from Client.MyQt.Section.QtMyPercentSection import PercentSection
from Client.MyQt.Section.QtMyVisitSection import VisitSection
from Client.test import try_except
from DataBase.sql_handler import ClientDataBase


class VisitTable(QWidget, Configurable):
    class Header(int):
        MONTH = 0
        DAY = 1
        WEEKDAY = 2
        LESSON = 3
        LESSONTYPE = 4

    def __default__(self):
        return {
            "table_header": {
                "lesson_info": {
                    str(VisitTable.Header.MONTH): True,
                    str(VisitTable.Header.LESSON): True,
                    str(VisitTable.Header.WEEKDAY): False,
                    str(VisitTable.Header.DAY): True,
                    str(VisitTable.Header.LESSONTYPE): True
                }
            }
        }

    @try_except
    def __init__(self, parent: QVBoxLayout, program: 'MyProgram', window_config: WindowConfig.Config):
        super().__init__()
        self.program = program
        self.db = program.db
        self._setup_config(window_config)
        self.inner_layout = QHBoxLayout()
        self.inner_layout.setSpacing(0)

        self.header_height = 0
        self.first = True

        # init sections
        self.visit_table = VisitSection()
        self.percent_table = PercentSection()
        self.home_work_table = HomeworkSection()

        # share scroll bar between sections
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

    @try_except
    def _setup_config(self, window_config: Config):
        self.window_config = window_config
        self.window_config.check(self)

    @try_except
    def rowCount(self):
        return self.visit_table.rowCount()

    @try_except
    def columnCount(self):
        print("visit table", self.visit_table.columnCount())
        return self.visit_table.columnCount()

    @try_except
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

    @try_except
    def show_header(self, i):
        if i == 1:
            self._show_day = not self._show_day

    @try_except
    def set_horizontal_header(self, lessons: list):
        self.lessons = lessons
        self.visit_table.setColumnCount(len(lessons))

        self.header_height = 5
        self.visit_table.setRowCount(self.header_height)

        item1 = QTableWidgetItem()
        item1.setText("Месяц")
        self.visit_table.setVerticalHeaderItem(VisitTable.Header.MONTH, item1)

        item2 = QTableWidgetItem()
        item2.setText("День")
        self.visit_table.setVerticalHeaderItem(VisitTable.Header.DAY, item2)

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
        self.percent_table.setRowCount(5)
        self.percent_table.setItem(0, 0, PercentHeaderItem([], PercentItem.Orientation.ByStudents))
        self.percent_table.setSpan(0, 0, 5, 1)

        self.header_height = 0

        lesson_info = self.window_config["table_header"]['lesson_info']
        print("lesson_info", lesson_info)
        for key in lesson_info:
            row = str(key)
            visible = lesson_info[key]

            self.visit_table.setRowHidden(int(row), not visible)
            self.percent_table.setRowHidden(int(row), not visible)

            self.visit_table.setRowHeight(int(row), 5)
            self.percent_table.setRowHeight(int(row), 5)

            if visible:
                self.header_height += 1

        # months = get_months(lessons)
        for column in range(len(lessons)):
            dt = datetime.datetime.strptime(lessons[column]["date"], "%d-%m-%Y %I:%M%p")

            self.visit_table.setColumnWidth(column, 5)

            self.visit_table.setItem(VisitTable.Header.MONTH, column,
                                     MonthTableItem(dt.month))
            self.visit_table.setItem(VisitTable.Header.DAY, column,
                                     LessonDateItem(dt, lessons[column]["id"], self.program))
            self.visit_table.setItem(VisitTable.Header.WEEKDAY, column,
                                     WeekDayItem(dt))
            self.visit_table.setItem(VisitTable.Header.LESSON, column,
                                     LessonNumberItem(dt))
            self.visit_table.setItem(VisitTable.Header.LESSONTYPE, column,
                                     LessonTypeItem(lessons[column]["type"], self.program))

        start = 0
        for column in range(len(lessons)):
            if self.visit_table.item(0, column).text() != self.visit_table.item(0, start).text():
                self.visit_table.setSpan(0, start, 1, column - start)
                start = column
                self.visit_table.setSpan(0, start, 1, len(lessons) - start)
            self.visit_table.setColumnWidth(column, 5)

    @try_except
    def add_student(self, student: dict, visitations: list):
        self.students.append(student)
        row = self.visit_table.rowCount()
        self.insertRow(row)

        # set row header
        header_item = StudentHeaderItem(self.db, student)
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

        items_list = []
        for col in range(self.columnCount()):
            items_list.append(self.visit_table.item(row, col))

        percent_item = PercentItem(items_list, PercentItem.Orientation.ByStudents)
        self.percent_table.setItem(row, 0, percent_item)

        header = self.percent_table.item(0, 0)
        header.percents.append(percent_item)

        self.visit_table.resizeRowsToContents()
        self.percent_table.resizeRowsToContents()

    @try_except
    def fill_percents_byStudent(self):
        current_row = self.rowCount()
        self.insertRow(current_row)

        vertical_percents = []

        for col in range(self.visit_table.columnCount()):
            item = PercentItem(
                [self.visit_table.item(row, col) for row in range(self.rowCount())],
                PercentItem.Orientation.ByLessons)
            self.visit_table.setItem(current_row, col, item)
            vertical_percents.append(item)

        self.visit_table.setVerticalHeaderItem(current_row, PercentHeaderItem(vertical_percents))

    @try_except
    def insertRow(self, index: int):
        self.visit_table.insertRow(index)
        self.percent_table.insertRow(index)
        # self.home_work_table.insertRow(index)

    @try_except
    def removeRow(self, index: int):
        self.visit_table.removeRow(index)
        self.percent_table.removeRow(index)
        # self.home_work_table.removeRow(index)

    @try_except
    def row(self, student_id: int) -> int:
        for row in range(self.rowCount()):
            item = self.visit_table.verticalHeaderItem(row)
            if type(item) == StudentHeaderItem:
                if item.student["id"] == student_id:
                    return row
        return -1

    @try_except
    def col(self, lesson_id) -> int:
        for col in range(self.columnCount()):
            if self.lessons[col]["id"] == lesson_id:
                return col
        return -1

    @try_except
    def new_visit(self, student_id, lesson_id):
        col = self.col(lesson_id)
        row = self.row(student_id)

        item = self.visit_table.item(row, col)
        if item.status == VisitItem.Status.Visited:
            QStatusMessage.instance().setText("Студент уже в отмечен")
        else:
            student = self.visit_table.verticalHeaderItem(row).student
            QStatusMessage.instance().setText(
                "Студент {} {} отмечен".format(student["last_name"], student["first_name"]))
            item.set_visit_status(VisitItem.Status.Visited)

            self.percent_table.item(row, 0).refresh()
            self.visit_table.item(self.rowCount() - 1, col).refresh()

    @try_except
    def ForEachRow(self, col_index, func):
        for i in range(self.visit_table.rowCount()):
            func(self.visit_table.item(i, col_index))

    @try_except
    def ForEachColumn(self, row_index, func):
        for i in range(self.visit_table.colorCount()):
            func(self.visit_table.item(row_index, i))
