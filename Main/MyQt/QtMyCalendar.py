import traceback
from datetime import datetime

from PyQt5.QtWidgets import QWidget, QVBoxLayout, QCalendarWidget, QComboBox, QHBoxLayout, QLabel, QPushButton

from Main import config
from Main.DataBase.sql_handler import DataBaseWorker
from Main.MyQt.QtMyStatusBar import QStatusMessage
from Main.MyQt.Time import from_index_to_time


class LessonDateChanger(QWidget):
    def __init__(self, date: datetime, lesson_id:int, parent:'MainWindow'=None):
        super().__init__()
        self._parent = parent
        self.lesson_id = lesson_id
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
        self.button.setStyleSheet(config.main_button_css)
        self.l.addWidget(self.button)

        self.setLayout(self.l)

    def accept(self):
        try:
            d = self.calendar.selectedDate()

            dd = datetime(d.year(), d.month(), d.day())
            dd += from_index_to_time(self.lesson_selector.currentIndex())
            QStatusMessage.instance().setText("Занятие перенесено на {}".format(dd))

            DataBaseWorker.instance().update_lesson_date(lesson_id=self.lesson_id, new_date=dd)

            from Main.MyQt.Window.QtMyMainWindow import MainWindow
            self.close()
            self._parent.refresh_table()
        except Exception:
            traceback.print_exc()
