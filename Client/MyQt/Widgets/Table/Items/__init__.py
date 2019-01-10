from PyQt5.QtGui import QColor, QPen
from PyQt5.QtWidgets import QTableWidgetItem

from Client.MyQt.ColorScheme import Color


class AbstractContextItem:
    def show_context_menu(self, pos):
        pass


class MyTableItem(QTableWidgetItem):
    """
    Base Table Item class
    """

    CurrentLessonColor = QColor("#ccccff")

    def __init__(self):
        super().__init__()
        self.color = "#FFFFFF"
        self.current = False

    def set_current_lesson(self, b: bool):
        """
        set item activated as current lesson
        :param b: boolean value
        """
        self.current = b
        self.update()

    def update(self):
        """
        abstract _method
        """
        pass


class IDraw:
    border_pen = QPen(Color.secondary_dark)
    border_pen.setWidthF(0.5)

    textPen = QPen(Color.text_color)

    cached = dict()

    def draw(self, painter, rect, highlighted=False, selected=False):
        raise NotImplementedError()
