from PyQt5.QtWidgets import QPushButton, QLineEdit, QWidget

from Main.DataBase.sql_handler import DataBaseWorker
from Main.MyQt.QtMyLoginInput import QLoginInput
from Main.MyQt.QtMyMainWindow import QMyMainWindow


class QAuthButton(QPushButton):
    def __init__(self, db:DataBaseWorker, login_input:QLoginInput, password_input:QLineEdit, parent:QWidget):
        super().__init__()
        self.parent = parent
        self.db = db
        self.login = login_input
        self.password = password_input

    def click(self):
        print(self.login_input.text(), self.password.text())
        if self.db.auth(card_id=self.login_input.text(), password=self.password.text()):
            self.parent = QMyMainWindow()