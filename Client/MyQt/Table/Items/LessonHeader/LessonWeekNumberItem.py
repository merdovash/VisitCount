from datetime import datetime

from PyQt5.QtCore import Qt

import Date
from Client.MyQt.Table.Items.LessonHeader.LessonHeaderItem import \
    LessonHeaderItem


class WeekNumber(LessonHeaderItem):
    def __init__(self, date: datetime):
        super().__init__()
        self.setTextAlignment(Qt.AlignCenter)
        self.setText(str(date.isocalendar()[1] - Date.start_week()))
