from typing import List

from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont
from PyQt5.QtWidgets import QTableWidgetItem


class IPercentItem():
    def refresh(self):
        raise NotImplementedError()


class PercentItem(IPercentItem, QTableWidgetItem):
    """
    represents items containing total amount of visitations related to total count of lessons by lesson or student
    """
    __items__: List[IPercentItem] = []

    class Font(int):
        Absolute = QFont("SansSerif", 7)
        Percent = QFont("SansSerif", 8)

    class Orientation(int):
        ByLessons = 0
        ByStudents = 1

    def __init__(self, items: list, orientation: 'PercentItem.Orientation', absolute=False, *__args):
        super().__init__(*__args)
        self.absolute = absolute
        self.items = items
        self.visit = 0
        self.total = 0
        self.orientation = orientation
        self.refresh()

        if self.orientation == PercentItem.Orientation.ByLessons:
            self.setTextAlignment(Qt.AlignCenter)
        else:
            self.setTextAlignment(Qt.AlignLeft)
        PercentItem.__items__.append(self)

    def calc(self):
        for item in self.items:
            self.total += item.visit_data[1]
            self.visit += item.visit_data[0]

    def refresh(self):
        self.calc()
        self.updateText()

    def updateText(self):
        if self.absolute:
            self.setText(str(self.visit))
            # self.setFont(PercentItem.Font.Absolute)
        else:
            self.setText("{}".format(round(self.visit * 100 / self.total) if self.total != 0 else 0))
            #self.setFont(PercentItem.Font.Percent)
