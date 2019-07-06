from typing import Callable

from PyQt5.QtWidgets import QGridLayout, QPushButton

from Client.MyQt.Widgets import BisitorWidget


class QAccentCancelButtons(BisitorWidget):
    def __init__(self, on_accept: Callable[[], None], on_cancel: Callable[[], None]):
        super().__init__()

        self.grid = QGridLayout()
        accept = QPushButton('Принять')
        accept.clicked.connect(on_accept)
        self.grid.addWidget(accept, 1, 0)

        cancel = QPushButton('Отменить')
        cancel.setObjectName('Cancel')
        cancel.clicked.connect(on_cancel)
        self.grid.addWidget(cancel, 1, 1)

        self.setLayout(self.grid)
