from PyQt5 import QtGui, QtCore
from PyQt5.QtCore import pyqtSignal, pyqtSlot

from Client.IProgram import IProgram
from Client.MyQt.Widgets.Network.Request import first_load
from Client.MyQt.Window import AbstractWindow
from Client.MyQt.Window.Auth.UiAuth import Ui_AuthWindow
from Client.Reader.Functor import OnRead
from Client.Reader.Functor.AuthProfessor import AuthProfessorOnRead
from DataBase2 import Auth
from Domain.Exception.Authentication import InvalidPasswordException, InvalidLoginException


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
            a = Auth.log_in(login, password)

            self.auth_success.emit(dict(login=login, password=password))
        except InvalidLoginException:
            self.centralwidget.layout().addWidget(
                first_load(self.program.host, login, password,
                           on_close=lambda: self.auth_success.emit(dict(login=login, password=password))))

    def keyPressEvent(self, a0: QtGui.QKeyEvent):
        print("keypressEvent", a0.key(), QtCore.Qt.Key_Enter)
        if a0.key() + 1 == QtCore.Qt.Key_Enter:
            self.auth()
