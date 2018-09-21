from datetime import datetime

from PyQt5 import QtCore
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QCalendarWidget, QComboBox, QHBoxLayout, QLabel, QPushButton

from Client.IProgram import IProgram
from Client.MyQt.Time import from_index_to_time
from Client.test import safe
from DataBase2 import Lesson


class LessonDateChanger(QWidget):
    def __init__(self, program: IProgram, date: datetime, lesson: Lesson):
        super().__init__(flags=QtCore.Qt.WindowStaysOnTopHint)
        self.program: IProgram = program
        self.lesson = lesson
        self.l = QVBoxLayout()

        self.calendar = QCalendarWidget()
        # self.calendar.setSelectedDate(QDate=QDate(date.year, date.month, date.day))
        self.l.addWidget(self.calendar)

        self.lesson_selector_layout = QHBoxLayout()
        self.l.addLayout(self.lesson_selector_layout)
        self.lesson_selector_layout.addWidget(QLabel("Выберете время занятия"))

        self.lesson_selector = QComboBox()
        self.lesson_selector.addItems(["1. 9:00", "2. 10:45", "3. 13:00", "4. 14:45", "5. 16:30", "6. 18:15"])

        self.lesson_selector_layout.addWidget(self.lesson_selector)

        self.button = QPushButton("Подтвердить")
        self.button.clicked.connect(self.accept)
        self.button.setStyleSheet("background-color: #ff8000; color: #ffffff; font-weight: bold;")
        self.l.addWidget(self.button)

        self.setLayout(self.l)

    @safe
    def accept(self, b=None):
        d = self.calendar.selectedDate()

        dd = datetime(d.year(), d.month(), d.day())
        dd += from_index_to_time(self.lesson_selector.currentIndex())
        self.program.window.message.emit("Занятие перенесено на {}".format(dd), False)

        self.lesson.date = dd

        self.program.window.centralWidget().refresh_table()
        self.close()
