from PyQt5.QtWidgets import QMessageBox


class QOkMsg(QMessageBox):
    def __init__(self, text, *__args):
        super().__init__(*__args)

        self.setStandardButtons(QMessageBox.Ok)
        self.button(QMessageBox.Ok).clicked.connect(self.close)

        self.setText(text)

    def showAsChild(self, *args):
        self.exec_()
