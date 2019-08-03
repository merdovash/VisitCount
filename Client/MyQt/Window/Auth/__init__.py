from PyQt5 import QtGui, QtCore
from PyQt5.QtCore import pyqtSignal, pyqtSlot

from Client.IProgram import IProgram
from Client.MyQt.Widgets import Message
from Client.MyQt.Widgets.Network.Request import RequestWidget
from Client.MyQt.Widgets.NewUserForm import NewUserForm
from Client.MyQt.Window import AbstractWindow
from Client.MyQt.Window.Auth.UiAuth import Ui_AuthWindow
from Client.MyQt.Window.Main import MainWindow
from DataBase2 import Auth
from Debug.WrongId import debug
from Domain.Exception.Authentication import InvalidLoginException
from Modules.FirstLoad.ClientSide import InitialDataLoader
from Parser import Args


class AuthWindow(AbstractWindow, Ui_AuthWindow):
    new_user_form = None

    def __init__(self, flags=None, *args, **kwargs):
        super().__init__(flags, *args, **kwargs)
        self.setupUi(self)
        self.setWindowTitle('СПбГУТ - Система учета посещаемости')
        self.retranslateUi(self)

        self.auth_btn.clicked.connect(self.auth)
        self.auth_success.connect(self.on_auth_success)
        self.dialog = None

        self.create_auth_btn.clicked.connect(self.show_form)

    # signals
    auth_success = pyqtSignal('PyQt_PyObject')

    # slots
    @pyqtSlot('PyQt_PyObject')
    def on_auth_success(self, auth):
        self.auth = Auth.log_in(**auth)
        self.professor = self.auth.user
        debug(self.auth.user)
        window = MainWindow(professor=self.professor)
        window.show()

        self.close()

    def auth(self, *args):
        login = self.login_input.login()
        password = self.password_input.text()
        if login == '' or password == '':
            Message().information(self, 'Вход в систему', 'Укажите логин и пароль.')
        else:
            try:
                a = Auth.log_in(login, password)

                self.auth_success.emit(dict(login=login, password=password))
            except InvalidLoginException:
                self.centralwidget.layout().addWidget(
                    RequestWidget(
                        InitialDataLoader(
                            login=login,
                            password=password,
                            host=Args().host),
                        text_button="Загрузить данные",
                        title="загрузка данных",
                        on_close=lambda: self.auth_success.emit(dict(login=login, password=password))
                    )
                )

    def keyPressEvent(self, a0: QtGui.QKeyEvent):
        if a0.key() + 1 == QtCore.Qt.Key_Enter:
            self.auth()

    def show_form(self):
        if self.new_user_form is None:
            self.new_user_form = NewUserForm()

        self.new_user_form.show()
