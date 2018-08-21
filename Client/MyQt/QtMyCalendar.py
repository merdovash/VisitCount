from datetime import datetime

from PyQt5 import QtCore
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QCalendarWidget, QComboBox, QHBoxLayout, QLabel, QPushButton

from Client.MyQt.Program import MyProgram
from Client.MyQt.QtMyStatusBar import QStatusMessage
from Client.MyQt.Time import from_index_to_time
from Client.test import try_except
from DataBase.sql_handler import ClientDataBase


class LessonDateChanger(QWidget):
    def __init__(self, db: ClientDataBase, date: datetime, lesson_id: int, program: MyProgram = None):
        super().__init__(flags=QtCore.Qt.WindowStaysOnTopHint)
        self.program: MyProgram = program
        self.lesson_id = lesson_id
        self.db: ClientDataBase = db
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
        self.button.setStyleSheet(self.db.config.main_button_css)
        self.l.addWidget(self.button)

        self.setLayout(self.l)

    @try_except
    def accept(self, b=None):
        d = self.calendar.selectedDate()

        dd = datetime(d.year(), d.month(), d.day())
        dd += from_index_to_time(self.lesson_selector.currentIndex())
        QStatusMessage.instance().setText("Занятие перенесено на {}".format(dd))

        self.db.update_lesson_date(lesson_id=self.lesson_id, new_date=dd)

        self.program.window.centralWidget().refresh_table()
        self.close()

