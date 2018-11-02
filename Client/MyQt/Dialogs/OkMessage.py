from PyQt5.QtWidgets import QMessageBox


class OkMessage(QMessageBox):
    def __init__(self, text, *__args):
        super().__init__(*__args)

        self.setStandardButtons(QMessageBox.Ok)

        self.setText(text)
