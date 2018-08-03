from PyQt5.QtWidgets import QDialog, QVBoxLayout, QLabel


class Server504(QDialog):
    def __init__(self, parent):
        super().__init__(parent)

        self.l = QVBoxLayout()

        self.text = QLabel("Не удается подключиться к серверу для подтверждения введенных данных.")
        self.l.addWidget(self.text)

        self.setLayout(self.l)
