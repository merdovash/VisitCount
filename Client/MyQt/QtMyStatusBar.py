from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont
from PyQt5.QtWidgets import QLabel


class QStatusMessage(QLabel):
    """

    contains label to display massages from program to user
    """

    def __init__(self, *__args):
        super().__init__(*__args)
        self.setToolTip("Текущий статус программы")
        self.setAlignment(Qt.AlignRight)
        self.setFont(QFont("", 16))
