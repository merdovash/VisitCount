import PyQt5

from PyQt5.QtCore import Qt
from PyQt5.QtGui import QColor
from PyQt5.QtWidgets import QTableWidgetItem, QMenu

from Main.MyQt.QtMyStatusBar import QStatusMessage
from Main.SerialsReader import getReader
from Main.DataBase.sql_handler import DataBaseWorker


class MyTableItem(QTableWidgetItem):
    def __init__(self):
        super().__init__()
        self.color = "#FFFFFF"
        self.current = False

    def current_lesson(self, b):
        self.current = b
        self.update()

    def update(self):
        pass


class VisitItem(MyTableItem):
    class Status(int):
        Visited = 1
        NoInfo = 2
        NotVisited = 0

    class Data(int):
        Completed = 1
        Visited = 0

    def __init__(self, status: Status):
        super().__init__()
        self.setTextAlignment(Qt.AlignCenter)
        self.status = status
        self.visit_data = [0, 0]
        self.update()

    def set_visit_status(self, status: Status):
        self.status = status
        self.update()

    def update(self):
        if self.status == VisitItem.Status.Visited:
            self.setText("+")
            self.color = "#ffff00"
            self.setBackground(QColor("#8BFFE5") if self.current else QColor(self.color))
            self.visit_data = [1, 1]
        elif self.status == VisitItem.Status.NotVisited:
            self.setText("-")
            self.setBackground(QColor("#8BFFE5") if self.current else QColor(self.color))
            self.visit_data = [0, 1]
        elif self.status == VisitItem.Status.NoInfo:
            self.setText("")
            self.setBackground(QColor("#8BFFE5") if self.current else QColor(self.color))
            self.visit_data = [0, 0]


class LessonTypeItem(QTableWidgetItem):
    def __init__(self, lesson_type: int):
        super().__init__()
        self.setTextAlignment(Qt.AlignCenter)
        lesson_type = int(lesson_type)
        if lesson_type == 0:
            self.setText("Л")
            self.setToolTip("Лекция")
        elif lesson_type == 1:
            self.setText("л")
            self.setToolTip("Лабораторная работа")
        else:
            self.setText("П")
            self.setToolTip("Практика")


month_names = "0,Январь,Февраль,Март,Апрель,Май,Июнь,Июль,Август,Сентябрь,Октябрь,Ноябрь,Декабрь".split(',')


class MonthTableItem(QTableWidgetItem):
    def __init__(self, month: int):
        super().__init__()
        self.setTextAlignment(Qt.AlignCenter)
        self.setText(month_names[month])


class PercentItem(QTableWidgetItem):
    def __init__(self, value=0):
        super().__init__()
        self.mask = "{0}%"

        self.setText(self.mask.format(value))

    def setValue(self, value):
        self.setText(self.mask.format(value))


class StudentHeaderItem(QTableWidgetItem):
    def __init__(self, student:dict, *__args):
        super().__init__(*__args)
        self.setText("{} {}. {}.".format(
                student["last_name"],
                student['first_name'][0],
                student["middle_name"][0]
            ))
        self.student = student

    def show_context_menu(self, pos):
        menu = QMenu()
        print(pos)
        menu.move(pos)
        menu.addAction("Зарегистрировать карту", self.register)
        menu.addAction("Показать номер карты", lambda: QStatusMessage.get().setText(self.student["card_id"]))
        menu.exec_()

    def register(self):
        self.r = getReader()
        self.r.method = self.reader_handler

    def reader_handler(self, card_id):
        if self.student["card_id"] is not None:
            QStatusMessage.get().setText("Студенту {} {} перезаписали номер карты".format(
                self.student["last_name"],
                self.student["first_name"]))
        else:
            QStatusMessage.get().setText("Студенту {} {} записали номер карты".format(
                self.student["last_name"],
                self.student["first_name"]))
        db = DataBaseWorker.get()
        db.add_card_id_to(card_id=card_id, student_id=self.student["id"])
        self.r.method = lambda x: 0
        self.card_id = card_id
