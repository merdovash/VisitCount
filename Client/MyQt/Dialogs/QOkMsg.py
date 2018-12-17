from PyQt5.QtWidgets import QMessageBox

from Client.MyQt.Window.interfaces import IChildWindow


class QOkMsg(QMessageBox, IChildWindow):
    def __init__(self, text, *__args):
        super().__init__(*__args)

        self.setStandardButtons(QMessageBox.Ok)
        self.button(QMessageBox.Ok).clicked.connect(self.closeSelf)

        self.setText(text)

    def showAsChild(self, *args):
        self.exec_()
