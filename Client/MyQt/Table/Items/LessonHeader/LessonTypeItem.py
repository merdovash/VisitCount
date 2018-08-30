from PyQt5 import QtGui
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QTableWidgetItem

from Client.MyQt.Table.Items import AbstractContextItem


class LessonTypeItem(QTableWidgetItem, AbstractContextItem):
    """
    item represents type of lesson
    """

    def __init__(self, lesson_type: int, program):
        super().__init__()
        self.program = program
        self.setTextAlignment(Qt.AlignCenter)
        lesson_type = int(lesson_type)
        if lesson_type == 0:
            self.setText("Л")
            self.setToolTip("Лекция")
        elif lesson_type == 1:
            self.setText("лр")
            self.setToolTip("Лабораторная работа")
        else:
            self.setText("П")
            self.setToolTip("Практика")

        self.setFont(QtGui.QFont("Times", weight=QtGui.QFont.Bold))

    def show_context_menu(self, pos):
        # TODO: make start and end function
        """
        override _method
        :param pos:
        """
        pass
        # if not self.program['marking_visits']:
        #     menu = QMenu()
        #     print(pos)
        #     menu.move(pos)
        #     action = QAction("Начать учет", self)
        #     menu.exec_()
