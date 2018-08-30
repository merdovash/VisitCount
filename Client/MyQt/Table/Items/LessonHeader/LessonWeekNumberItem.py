from datetime import datetime

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QTableWidgetItem

import Date


class WeekNumber(QTableWidgetItem):
    def __init__(self, date: datetime):
        super().__init__()
        self.setTextAlignment(Qt.AlignCenter)
        self.setText(str(date.isocalendar()[1] - Date.start_week()))
