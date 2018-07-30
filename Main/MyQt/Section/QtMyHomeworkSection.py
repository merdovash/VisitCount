from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QTableWidget, QAbstractItemView


class HomeworkSection(QTableWidget):
    def __init__(self, *__args):
        super().__init__(*__args)

        self.setMaximumWidth(400)
        self.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)