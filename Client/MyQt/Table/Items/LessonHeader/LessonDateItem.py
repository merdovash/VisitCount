from datetime import datetime
from typing import List

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QMenu, QTableWidgetItem

from Client.IProgram import IProgram
from Client.MyQt.Table.Calendar import LessonDateChanger
from Client.MyQt.Table.Items import AbstractContextItem
from Client.test import safe
from DataBase2 import Lesson


class LessonDateItem(QTableWidgetItem, AbstractContextItem):
    """
    item represent day of month of lesson
    """

    def __init__(self, date: datetime, lesson: Lesson, index: int, program: IProgram, parent):
        super().__init__()
        self.program: IProgram = program
        self.parent = parent
        self.date = date
        self.lesson = lesson
        self.setTextAlignment(Qt.AlignCenter)
        self.setText(str(date.day))

        self.visits: List['VisitItem'] = self.parent.get_column(index)

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
            # menu.move(pos)
            menu.addAction("Перенести занятие", self._move_lesson)
            if self.lesson.completed:
                menu.addAction("Отменить факт проведения занятия", self._uncomplete_lesson)
            menu.exec_(pos)

    @safe
    def _move_lesson(self):
        self.calendar = LessonDateChanger(self.program, self.date, self.lesson)
        self.calendar.show()

    def _uncomplete_lesson(self):

        self.lesson.completed = False

        for vsit_item in self.visits:
            vsit_item._del_visit_by_professor()
