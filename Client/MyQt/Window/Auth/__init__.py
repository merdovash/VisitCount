from PyQt5 import QtGui, QtCore
from PyQt5.QtCore import pyqtSignal, pyqtSlot

from Client.IProgram import IProgram
from Client.MyQt.Widgets.Network.Request import first_load
from Client.MyQt.Widgets.NewUserForm import NewUserForm
from Client.MyQt.Window import AbstractWindow
from Client.MyQt.Window.Auth.UiAuth import Ui_AuthWindow
from DataBase2 import Auth
from Domain.Exception.Authentication import InvalidPasswordException, InvalidLoginException


class AuthWindow(AbstractWindow, Ui_AuthWindow):
    new_user_form = None

    def __init__(self, program, flags=None, *args, **kwargs):
        super().__init__(flags, *args, **kwargs)

        self.setStyleSheet(kwargs.get('css'))

        self.setupUi(self)
        self.retranslateUi(self)

        self.program: IProgram = program

        self.auth_btn.clicked.connect(self.auth)
        self.auth_success.connect(self.on_auth_success)
        self.dialog = None

        self.create_auth_btn.clicked.connect(self.show_form)

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
        if a0.key() + 1 == QtCore.Qt.Key_Enter:
            self.auth()

    def show_form(self):
        if self.new_user_form is None:
            self.new_user_form = NewUserForm()

        self.new_user_form.show()
