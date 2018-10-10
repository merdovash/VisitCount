from datetime import datetime

from PyQt5.QtCore import Qt

from Client.MyQt.Table.Items.LessonHeader.LessonHeaderItem import \
    LessonHeaderItem


class WeekDayItem(LessonHeaderItem):
    """
    item represents week day of lesson
    """
    rule = ["пн", "вт", "ср", "чт", "пт", "сб", "вс"]

    def __init__(self, date: datetime):
        super().__init__()
        self.setTextAlignment(Qt.AlignCenter)
        self.setText(str(WeekDayItem.rule[date.weekday()]))
