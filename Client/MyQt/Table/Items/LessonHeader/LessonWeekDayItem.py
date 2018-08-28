from datetime import datetime

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QTableWidgetItem


class WeekDayItem(QTableWidgetItem):
    """
    item represents week day of lesson
    """
    rule = ["пн", "вт", "ср", "чт", "пт", "сб", "вс"]

    def __init__(self, date: datetime):
        super().__init__()
        self.setTextAlignment(Qt.AlignCenter)
        self.setText(str(WeekDayItem.rule[date.weekday()]))
