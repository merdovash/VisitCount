from typing import Callable

from PyQt5.QtWidgets import QWidget, QGridLayout, QPushButton


class QAccentCancelButtons(QWidget):
    def __init__(self, on_accept: Callable[[], None], on_cancel: Callable[[], None]):
        super().__init__()

        self.grid = QGridLayout()
        accept = QPushButton('Принять')
        accept.clicked.connect(on_accept)
        self.grid.addWidget(accept, 1, 0)

        cancel = QPushButton('Отменить')
        cancel.clicked.connect(on_cancel)
        self.grid.addWidget(cancel, 1, 1)

        self.setLayout(self.grid)
