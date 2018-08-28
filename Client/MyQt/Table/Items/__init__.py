from PyQt5.QtGui import QColor
from PyQt5.QtWidgets import QTableWidgetItem

from Client.test import safe


class AbstractContextItem:
    def show_context_menu(self, pos):
        pass


class MyTableItem(QTableWidgetItem):
    """
    Base Table Item class
    """

    CurrentLessonColor = QColor("#ccccff")

    @safe
    def __init__(self):
        super().__init__()
        self.color = "#FFFFFF"
        self.current = False

    @safe
    def set_current_lesson(self, b: bool):
        """
        set item activated as current lesson
        :param b: boolean value
        """
        self.current = b
        self.update()

    @safe
    def update(self):
        """
        abstract _method
        """
        pass
