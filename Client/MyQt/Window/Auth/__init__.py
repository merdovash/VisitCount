from PyQt5 import QtGui, QtCore
from PyQt5.QtCore import Qt, pyqtSignal, pyqtSlot
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLineEdit, QFormLayout, QLabel, QPushButton, QDialog, \
    QErrorMessage

from Client.Domain.Authentication import Authentication
from Client.Domain.Exception import NoSuchUserException
from Client.Domain.ServerRequest.FirstLoad import FirstLoad
from Client.IProgram import IProgram
from Client.MyQt.Window import AbstractWindow
from Client.MyQt.Window.Auth.QtMyLoginInput import LoginInput
from Client.MyQt.Window.Auth.UiAuth import Ui_AuthWindow
from Client.test import safe
# from DataBase.Authentication import Authentication
# from DataBase.ClentDataBase import ClientDataBase
# from Modules.FirstLoad.ClientSide import FirstLoad
from DataBase2 import Auth


class AuthWindow(AbstractWindow, Ui_AuthWindow):

    def __init__(self, program, flags=None, *args, **kwargs):
        super().__init__(flags, *args, **kwargs)
        self.setupUi(self)
        self.retranslateUi(self)

        self.program: IProgram = program

        self.auth_btn.clicked.connect(self.auth)
        self.auth_success.connect(self.on_auth_success)
        self.dialog = None

    # signals
    auth_success = pyqtSignal('PyQt_PyObject')

    # slots
    @pyqtSlot('PyQt_PyObject')
    def on_auth_success(self, auth):
        self.program.auth_success(auth)

    def showDialog(self, d: QDialog):
        self.dialog = d
        self.dialog.show()

    def showError(self, msg):
        self.dialog = QErrorMessage()
        self.dialog.showMessage(msg)

    def setup_serial(self):
        def imaged_value(prof_card_id):
            print(int(prof_card_id))
            prof = self.db.get_professors(card_id=int(prof_card_id))
            if len(prof) == 0:
                self.login_input.setText(prof_card_id)
            else:
                name = prof[0]['last_name'] + ' ' + prof[0]['first_name'] + ' ' + prof[0]['middle_name']
                self.login_input.set_image_text(prof_card_id, name)

        if self.program.reader() is not None:
            self.program.reader().on_read(imaged_value)

    @safe
    def auth(self, *args):
        try:
            a = Authentication(login=self.login_input.login(), password=self.password_input.text())

            self.auth_success.emit(a)
        except NoSuchUserException:
            FirstLoad(program=self.program,
                      auth=Auth(login=self.login_input.login(), password=self.password_input.text()),
                      login=self.login_input.login(),
                      password=self.password_input.text(),
                      on_finish=self.auth_success.emit)

    def keyPressEvent(self, a0: QtGui.QKeyEvent):
        print("keypressEvent", a0.key(), QtCore.Qt.Key_Enter)
        if a0.key() + 1 == QtCore.Qt.Key_Enter:
            self.auth()
