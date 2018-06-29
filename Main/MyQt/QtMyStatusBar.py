from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont
from PyQt5.QtWidgets import QLabel


class QStatusMessage(QLabel):
    """
    SINGLETON

    contains label to display massages from program to user
    """
    inst = None

    @staticmethod
    def get():
        if QStatusMessage.inst is None:
            QStatusMessage.inst = QStatusMessage()
        return QStatusMessage.inst

    def __init__(self, *__args):
        if QStatusMessage.inst is None:
            super().__init__(*__args)
            self.setToolTip("Текущий статус программы")
            self.setAlignment(Qt.AlignRight)
            self.setFont(QFont("", 16))
        else:
            raise Exception("too much instances")
