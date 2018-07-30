import datetime
import traceback

from PyQt5.QtGui import QResizeEvent
from PyQt5.QtWidgets import QWidget, QHBoxLayout, QTableWidgetItem, QVBoxLayout, QMainWindow

from Main.Configuartion.Configurable import Configurable
from Main.Configuartion.WindowConfig import Config
from Main.MyQt.QtMyStatusBar import QStatusMessage
from Main.MyQt.QtMyWidgetItem import VisitItem, LessonTypeItem, MonthTableItem, \
    StudentHeaderItem, \
    PercentItem, PercentHeaderItem, LessonDateItem, LessonNumberItem, WeekDayItem
from Main.MyQt.Section.QtMyHomeworkSection import HomeworkSection
from Main.MyQt.Section.QtMyPercentSection import PercentSection
from Main.MyQt.Section.QtMyVisitSection import VisitSection


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

    def __init__(self, parent: QVBoxLayout, MainWindow: QMainWindow, window_config: Config):
        super().__init__(MainWindow)
        self._parent = MainWindow
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
        self.scroll_bar = self.visit_table.verticalScrollBar()
        self.percent_table.setVerticalScrollBar(self.scroll_bar)
        self.home_work_table.setVerticalScrollBar(self.scroll_bar)

        # add widgets to layout
        self.inner_layout.addWidget(self.scroll_bar)
        self.inner_layout.addWidget(self.visit_table)
        self.inner_layout.addWidget(self.percent_table)
        self.inner_layout.addWidget(self.home_work_table)

        self.students = []
        self.lessons = []

        parent.addLayout(self.inner_layout)

        self.lessons = None

    def _setup_config(self, window_config: Config):
        self.window_config = window_config
        self.window_config.check(self)

    def resizeEvent(self, a0: QResizeEvent):
        super().resizeEvent(a0)
        print("resized")
        # TODO: resize

        try:
            print(self.visit_table.verticalScrollBar())
            self.scroll_bar = self.visit_table.verticalScrollBar()
        # # share scroll bar between sections
        #    scroll_bar = self.visit_table.verticalScrollBar()
        #    self.percent_table.setVerticalScrollBar(scroll_bar)
        #    self.home_work_table.setVerticalScrollBar(scroll_bar)

        #    # self.inner_layout.removeWidget(self.scroll_bar)
        #    self.inner_layout.insertWidget(0, scroll_bar)
        #    self.scroll_bar = scroll_bar
        except Exception as e:
            traceback.print_exc()

    def rowCount(self):
        return self.visit_table.rowCount()

    def columnCount(self):
        return self.visit_table.columnCount()

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

    def show_header(self, i):
        if i == 1:
            self._show_day = not self._show_day

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

        try:
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
        except Exception:
            traceback.print_exc()

        # months = get_months(lessons)
        try:
            for column in range(len(lessons)):
                dt = datetime.datetime.strptime(lessons[column]["date"], "%d-%m-%Y %I:%M%p")

                self.visit_table.setColumnWidth(column, 5)

                self.visit_table.setItem(VisitTable.Header.MONTH, column,
                                         MonthTableItem(dt.month))
                self.visit_table.setItem(VisitTable.Header.DAY, column,
                                         LessonDateItem(dt, lessons[column]["id"], self._parent))
                self.visit_table.setItem(VisitTable.Header.WEEKDAY, column,
                                         WeekDayItem(dt))
                self.visit_table.setItem(VisitTable.Header.LESSON, column,
                                         LessonNumberItem(dt))
                self.visit_table.setItem(VisitTable.Header.LESSONTYPE, column,
                                         LessonTypeItem(lessons[column]["type"]))
        except Exception:
            traceback.print_exc()

        start = 0
        for column in range(len(lessons)):
            if self.visit_table.item(0, column).text() != self.visit_table.item(0, start).text():
                self.visit_table.setSpan(0, start, 1, column - start)
                start = column
                self.visit_table.setSpan(0, start, 1, len(lessons) - start)
            self.visit_table.setColumnWidth(column, 5)

    def add_student(self, student: dict, visitations: list):
        self.students.append(student)
        row = self.visit_table.rowCount()
        self.insertRow(row)

        # set row header
        header_item = StudentHeaderItem(student)
        self.visit_table.setVerticalHeaderItem(row, header_item)

        completed_lessons = list(filter(lambda x: x["completed"] == 1, self.lessons))
        # print(completed_lessons)
        # fill row and find percents
        visitations_id = [i["id"] for i in visitations]
        for j in range(len(self.lessons)):
            try:
                if self.lessons[j] in completed_lessons:
                    if self.lessons[j]["id"] in visitations_id:
                        item = VisitItem(self.visit_table, VisitItem.Status.Visited)
                    else:
                        item = VisitItem(self.visit_table, VisitItem.Status.NotVisited)
                else:
                    item = VisitItem(self.visit_table, VisitItem.Status.NoInfo)
                item.student = student
                item.lesson = self.lessons[j]
                self.visit_table.setItem(row, j, item)
            except Exception as e:
                print("ERROR: add student -> fill row: ", e)

        percent_item = PercentItem([self.visit_table.item(row, col) for col in range(self.columnCount())],
                                   PercentItem.Orientation.ByStudents)
        self.percent_table.setItem(row, 0, percent_item)

        header = self.percent_table.item(0, 0)
        header.percents.append(percent_item)

        self.visit_table.resizeRowsToContents()
        self.percent_table.resizeRowsToContents()

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

    def insertRow(self, index: int):
        print(self.visit_table.rowCount(), index)
        self.visit_table.insertRow(index)
        self.percent_table.insertRow(index)
        # self.home_work_table.insertRow(index)

    def removeRow(self, index: int):
        self.visit_table.removeRow(index)
        self.percent_table.removeRow(index)
        # self.home_work_table.removeRow(index)

    def row(self, student_id: int) -> int:
        for row in range(self.rowCount()):
            item = self.visit_table.verticalHeaderItem(row)
            if type(item) == StudentHeaderItem:
                if item.student["id"] == student_id:
                    return row
        return -1

    def col(self, lesson_id) -> int:
        for col in range(self.columnCount()):
            if self.lessons[col]["id"] == lesson_id:
                return col
        return -1

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

    def ForEachRow(self, col_index, func):
        for i in range(self.visit_table.rowCount()):
            func(self.visit_table.item(i, col_index))

    def ForEachColumn(self, row_index, func):
        for i in range(self.visit_table.colorCount()):
            func(self.visit_table.item(row_index, i))
