import datetime

from PyQt5.QtCore import Qt, QPoint
from PyQt5.QtGui import QResizeEvent
from PyQt5.QtWidgets import QTableWidget, QWidget, QHBoxLayout, QTableWidgetItem, QVBoxLayout

from Main.MyQt.QtMyWidgetItem import VisitItem, LessonTypeItem, PercentItem, MonthTableItem, StudentHeaderItem


class VisitTable(QWidget):
    def __init__(self, parent: QVBoxLayout):
        super().__init__()
        self.l = QHBoxLayout()
        self.l.setSpacing(0)
        self.visit_table = QTableWidget()
        self.visit_table.horizontalHeader().setVisible(False)
        self.visit_table.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.visit_table.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
        self.visit_table.verticalHeader().sectionClicked.connect(self.vertical_header_click)
        headers = self.visit_table.verticalHeader()
        headers.setContextMenuPolicy(Qt.CustomContextMenu)
        headers.customContextMenuRequested.connect(self.vertical_header_click)
        self.scroll_bar = self.visit_table.verticalScrollBar()

        self.percent_table = QTableWidget()
        self.percent_table.setFixedWidth(60)
        self.percent_table.setVerticalScrollBar(self.scroll_bar)
        self.percent_table.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.percent_table.verticalHeader().setVisible(False)
        self.percent_table.horizontalHeader().setVisible(False)
        self.percent_table.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOn)

        self.home_work_table = QTableWidget()
        self.home_work_table.setVerticalScrollBar(self.scroll_bar)
        self.home_work_table.setMaximumWidth(400)
        self.percent_table.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOn)

        self.l.addWidget(self.scroll_bar)
        self.l.addWidget(self.visit_table)
        self.l.addWidget(self.percent_table)
        self.l.addWidget(self.home_work_table)

        self.students = []
        self.lessons = []

        parent.addLayout(self.l)

        self.lessons = None
        self._init = True

    def vertical_header_click(self, event:QPoint):
        print("he")
        index = self.visit_table.indexAt(event)
        row = index.row()
        item = self.visit_table.verticalHeaderItem(row)
        if type(item) == StudentHeaderItem:
            real_pos = event.__pos__()+self.visit_table.pos()
            item.show_context_menu(real_pos)
        else:
            print("hello2")

    def resizeEvent(self, a0: QResizeEvent):
        super().resizeEvent(a0)
        print("resized")
        # TODO: resize
        # if self._init:
        #     try:
        #         self.l.removeWidget(self.scroll_bar)
        #         self.scroll_bar = self.visit_table.verticalScrollBar()
        #         self.percent_table.setVerticalScrollBar(self.scroll_bar)
        #         self.home_work_table.setVerticalScrollBar(self.scroll_bar)
        #         self.l.insertWidget(0, self.scroll_bar)
        #     except Exception as e:
        #         print(e)

    def rowCount(self):
        return self.visit_table.rowCount()

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
        self.percent_table.setItem(0, 0, QTableWidgetItem("Итого"))
        self.percent_table.setSpan(0, 0, 3, 1)

    def add_student(self, student: dict, visitations: list):
        self.students.append(student)
        current_row = self.visit_table.rowCount()
        self.visit_table.insertRow(current_row)
        self.percent_table.insertRow(current_row)

        # set row header
        item = StudentHeaderItem(student)
        self.visit_table.setVerticalHeaderItem(current_row, item)

        completed_lessons = list(filter(lambda x: x["completed"] == 1, self.lessons))
        print(completed_lessons)
        # fill row and find percents
        visit_count = 0
        visitations_id = [i["lesson_id"] for i in visitations]
        for j in range(len(self.lessons)):
            try:
                if self.lessons[j] in completed_lessons:
                    if self.lessons[j]["id"] in visitations_id:
                        item = VisitItem(VisitItem.Status.Visited)
                    else:
                        item = VisitItem(VisitItem.Status.NotVisited)
                    visit_count += 1 if self.lessons[j]["id"] in visitations_id else 0
                else:
                    item = VisitItem(VisitItem.Status.NoInfo)
                self.visit_table.setItem(current_row, j, item)
            except Exception as e:
                print("ERROR: add student -> fill row: ", e)

        self.percent_table.setItem(current_row,
                                   0,
                                   PercentItem(str(round(100 * visit_count / len(completed_lessons)))))

        self.visit_table.resizeRowsToContents()
        self.percent_table.resizeRowsToContents()

    def recalculate_percents(self, student_index=None):
        def get_percent(v_row: int) -> str:
            visit, total = 0, 0
            for col_index in range(self.visit_table.columnCount()):
                if self.visit_table.item(v_row, col_index) is not None:
                    item = self.visit_table.item(v_row, col_index)
                    if type(item) is VisitItem:
                        total += item.visit_data[VisitItem.Data.Completed]
                        visit += item.visit_data[VisitItem.Data.Visited]
            if total != 0:
                r = round(100 * visit / total)
            else:
                r = 0
            return r

        if student_index is None:
            for i in range(len(self.students)):
                item = self.percent_table.item(3 + i, 0)
                if type(item) is PercentItem:
                    self.percent_table.item(3 + i, 0).setValue(get_percent(3 + i))
            self.percent_table.dataChanged(self.percent_table.model().index(3, 0),
                                           self.percent_table.model().index(3 + len(self.students), 0))
        else:
            item = self.percent_table.item(3 + student_index, 0)
            if type(item) is PercentItem:
                item.setValue(get_percent(3 + student_index))
                self.percent_table.dataChanged(self.percent_table.model().index(3 + student_index, 0),
                                               self.percent_table.model().index(3 + student_index, 0))
            else:
                print("ERROR: trying to recalculate percents on a " + student_index + " row")

    def columnForEach(self, col_index, func: callable):
        for i in range(self.visit_table.rowCount()):
            func(self.visit_table.item(i, col_index))

    def rowForEach(self, row_index, func: callable):
        for i in range(self.visit_table.colorCount()):
            func(self.visit_table.item(row_index, i))
