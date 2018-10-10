from PyQt5.QtGui import QColor
from PyQt5.QtWidgets import QTableWidgetItem


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
