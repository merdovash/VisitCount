from typing import List

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QTableWidgetItem

from Client.MyQt.ColorScheme import Color
from Client.MyQt.Widgets.Table.Items import IDraw


class PercentItem(IDraw, QTableWidgetItem):
    """
    represents items containing total amount of visitations related to total count of lessons by lesson or student
    """

    def draw(self, painter, rect, highlighted=False):
        painter.fillRect(rect, self.get_color(highlighted))

        painter.setPen(self.textPen)
        painter.drawText(rect, Qt.AlignCenter, self.text())

        painter.setPen(self.border_pen)
        painter.drawRect(rect)

    def get_color(self, highlighted):
        color = Color.secondary_light
        if highlighted:
            color = Color.to_accent(color)
        return color

    class Orientation(int):
        ByLessons = 0
        ByStudents = 1

    def __init__(self, items: List['VisitItem'], orientation: int, absolute):
        super().__init__()
        self.absolute = absolute

        self.items: List['VisitItem'] = items
        for visit_item in self.items:
            assert hasattr(visit_item, 'info_changed')
            visit_item.info_changed += self.calc

        self.visit = 0
        self.total = 0

        self.orientation = orientation

        self.calc()

        if self.orientation == PercentItem.Orientation.ByLessons:
            self.setTextAlignment(Qt.AlignCenter)
        else:
            self.setTextAlignment(Qt.AlignLeft)

    def calc(self):
        self.visit = 0
        self.total = 0
        for item in self.items:
            self.total += item.visit_data[1]
            self.visit += item.visit_data[0]

        if self.absolute:
            text = str(self.visit)
        else:
            try:
                text = str(round(self.visit / self.total * 100, 0))
            except ZeroDivisionError:
                text = "-"

        self.setText(text)


class HorizontalSum(PercentItem):
    def __init__(self, items: List['VisitItem'], absolute):
        super().__init__(items, PercentItem.Orientation.ByLessons, absolute=absolute)


class VerticalSum(PercentItem):
    def __init__(self, items: List['VisitItem'], absolute):
        super().__init__(items, PercentItem.Orientation.ByStudents, absolute=absolute)
