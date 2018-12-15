from PyQt5 import QtGui, QtCore
from PyQt5.QtCore import pyqtSignal, pyqtSlot

from Client.IProgram import IProgram
from Client.MyQt.Window import AbstractWindow
from Client.MyQt.Window.Auth.UiAuth import Ui_AuthWindow
from Client.Reader.Functor import OnRead
from Client.Reader.Functor.AuthProfessor import AuthProfessorOnRead
from Domain import Action
from Domain.Action import NetAction, InvalidLoginException, InvalidPasswordException


# from DataBase.Authentication import Authentication
# from DataBase.ClentDataBase import ClientDataBase
# from Modules.FirstLoad.ClientSide import FirstLoad


class AuthWindow(AbstractWindow, Ui_AuthWindow):

    def __init__(self, program, flags=None, *args, **kwargs):
        super().__init__(flags, *args, **kwargs)

        self.setStyleSheet(kwargs.get('css'))

        self.setupUi(self)
        self.retranslateUi(self)

        self.program: IProgram = program

        self.auth_btn.clicked.connect(self.auth)
        self.auth_success.connect(self.on_auth_success)
        self.dialog = None

        OnRead.prepare(program, self, program.session, window=self)

        if program.reader() is not None:
            self.program.reader().on_read(AuthProfessorOnRead())

    # signals
    auth_success = pyqtSignal('PyQt_PyObject')

    # slots
    @pyqtSlot('PyQt_PyObject')
    def on_auth_success(self, auth):
        self.program.auth_success(auth)

    def auth(self, *args):
        login = self.login_input.login()
        password = self.password_input.text()
        try:
            a = Action.log_in(login, password)

            self.auth_success.emit(dict(login=login, password=password))
        except InvalidLoginException:
            NetAction.first_load(login, password, self.program.host,
                                 on_finish=self.auth_success.emit,
                                 on_error=self.ok_message.emit)
        except InvalidPasswordException as e:
            self.ok_message.emit(str(e))

    def keyPressEvent(self, a0: QtGui.QKeyEvent):
        print("keypressEvent", a0.key(), QtCore.Qt.Key_Enter)
        if a0.key() + 1 == QtCore.Qt.Key_Enter:
            self.auth()
