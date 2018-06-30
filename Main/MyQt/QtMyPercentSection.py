from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QTableWidget, QAbstractItemView


class PercentSection(QTableWidget):
    def __init__(self, *__args):
        super().__init__(*__args)

        self.setFixedWidth(60)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.verticalHeader().setVisible(False)
        self.horizontalHeader().setVisible(False)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
        self.setEditTriggers(QAbstractItemView.NoEditTriggers)