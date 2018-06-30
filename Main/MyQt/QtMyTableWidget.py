import datetime

from PyQt5.QtCore import Qt
from PyQt5.QtGui import QResizeEvent
from PyQt5.QtWidgets import QTableWidget, QWidget, QHBoxLayout, QTableWidgetItem, QVBoxLayout, QAbstractItemView

from Main.MyQt.QtMyHomeworkSection import HomeworkSection
from Main.MyQt.QtMyPercentSection import PercentSection
from Main.MyQt.QtMyStatusBar import QStatusMessage
from Main.MyQt.QtMyVisitSection import VisitSection
from Main.MyQt.QtMyWidgetItem import VisitItem, LessonTypeItem, MonthTableItem, \
    StudentHeaderItem, \
    PercentItem, PercentHeaderItem


class VisitTable(QWidget):
    def __init__(self, parent: QVBoxLayout):
        super().__init__()
        self.inner_layout = QHBoxLayout()
        self.inner_layout.setSpacing(0)
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
        self._init = True

    def resizeEvent(self, a0: QResizeEvent):
        super().resizeEvent(a0)
        print("resized")
        # TODO: resize
        # if self._init:
        #     try:
        #         self.inner_layout.removeWidget(self.scroll_bar)
        #         self.scroll_bar = self.visit_table.verticalScrollBar()
        #         self.percent_table.setVerticalScrollBar(self.scroll_bar)
        #         self.home_work_table.setVerticalScrollBar(self.scroll_bar)
        #         self.inner_layout.insertWidget(0, self.scroll_bar)
        #     except Exception as e:
        #         print(e)

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

    def set_horizontal_header(self, lessons: list):
        self.lessons = lessons
        self.visit_table.setColumnCount(len(lessons))

        self.visit_table.setRowCount(3)
        item1 = QTableWidgetItem()
        item1.setText("Месяц")
        self.visit_table.setVerticalHeaderItem(0, item1)
        item2 = QTableWidgetItem()
        item2.setText("День")
        self.visit_table.setVerticalHeaderItem(1, item2)
        item3 = QTableWidgetItem()
        item3.setText("Тип занятия")
        self.visit_table.setVerticalHeaderItem(2, item3)

        # months = get_months(lessons)
        for i in range(len(lessons)):
            dt = datetime.datetime.strptime(lessons[i]["date"], "%d-%m-%Y %I:%M%p")

            self.visit_table.setItem(0, i, MonthTableItem(dt.month))
            self.visit_table.setItem(1, i, QTableWidgetItem(str(dt.day)))
            self.visit_table.setItem(2, i, LessonTypeItem(lessons[i]["type"]))
            self.visit_table.setColumnWidth(i, 20)

        start = 0
        for i in range(len(lessons)):
            self.visit_table.setColumnWidth(i, 20)
            if self.visit_table.item(0, i).text() != self.visit_table.item(0, start).text():
                self.visit_table.setSpan(0, start, 1, i - start)
                start = i
                self.visit_table.setSpan(0, start, 1, len(lessons) - start)

        self.percent_table.setColumnCount(1)
        self.percent_table.setRowCount(3)
        self.percent_table.setItem(0, 0, PercentHeaderItem([], PercentItem.Orientation.ByStudents))
        self.percent_table.setSpan(0, 0, 3, 1)

    def add_student(self, student: dict, visitations: list):
        self.students.append(student)
        row = self.visit_table.rowCount()
        self.insertRow(row)

        # set row header
        header_item = StudentHeaderItem(student)
        self.visit_table.setVerticalHeaderItem(row, header_item)

        completed_lessons = list(filter(lambda x: x["completed"] == 1, self.lessons))
        print(completed_lessons)
        # fill row and find percents
        visitations_id = [i["lesson_id"] for i in visitations]
        for j in range(len(self.lessons)):
            try:
                if self.lessons[j] in completed_lessons:
                    if self.lessons[j]["id"] in visitations_id:
                        item = VisitItem(VisitItem.Status.Visited)
                    else:
                        item = VisitItem(VisitItem.Status.NotVisited)
                else:
                    item = VisitItem(VisitItem.Status.NoInfo)
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
