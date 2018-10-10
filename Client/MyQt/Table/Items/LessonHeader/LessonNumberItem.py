from datetime import datetime

from PyQt5.QtCore import Qt

from Client.MyQt.Table.Items.LessonHeader.LessonHeaderItem import \
    LessonHeaderItem
from Client.MyQt.Time import from_time_to_index


class LessonNumberItem(LessonHeaderItem):
    """
    item represents serial number of lesson
    """

    def __init__(self, date: datetime):
        super().__init__()
        self.setTextAlignment(Qt.AlignCenter)
        self.setText(str(from_time_to_index(date)))
