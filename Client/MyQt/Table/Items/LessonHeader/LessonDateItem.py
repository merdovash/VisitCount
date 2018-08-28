from datetime import datetime

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QMenu, QTableWidgetItem

from Client.MyQt.Table.Calendar import LessonDateChanger
from Client.MyQt.Table.Items import AbstractContextItem
from Client.test import safe


class LessonDateItem(QTableWidgetItem, AbstractContextItem):
    """
    item represent day of month of lesson
    """

    def __init__(self, date: datetime, lesson_id: int, program):
        super().__init__()
        self.program = program
        self.table_widget = self.program.window.centralWidget()
        self.date = date
        self.lesson_id = lesson_id
        self.setTextAlignment(Qt.AlignCenter)
        self.setText(str(date.day))

    @safe
    def show_context_menu(self, pos):
        """
        override base _method

        show context menu:
            1) change date of lesson
        :param pos:
        """
        if not self.program['marking_visits']:
            menu = QMenu()
            menu.move(pos)
            menu.addAction("Перенести занятие", self._move_lesson)
            menu.exec_()

    @safe
    def _move_lesson(self):
        self.calendar = LessonDateChanger(self.program.db, self.date, self.lesson_id, self.program)
        self.calendar.show()
