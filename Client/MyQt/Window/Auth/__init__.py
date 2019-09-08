from PyQt5 import QtGui, QtCore
from PyQt5.QtCore import pyqtSignal, pyqtSlot

from Client.MyQt.Widgets import Message, BisitorWidget
from Client.MyQt.Window.Main import MainWindow
from Client.Settings import Settings
from Domain.Exception import BisitorException
from Domain.Exception.Authentication import InvalidLoginException

from Modules.API.User.FirstLoad import FirstLoad
from Modules.API.User.Settings import SettingsAPI


class AuthWindow(BisitorWidget):
    new_user_form = None

    def __init__(self, flags=None, *args, **kwargs):
        from PyQt5.QtCore import Qt, QSize
        from PyQt5.QtWidgets import QPushButton, QLineEdit, QLabel, QGridLayout, QStyle, QApplication
        from Client.MyQt.Widgets.LoginInput import QLoginInput

        super().__init__(flags, *args, **kwargs)
        grid = QGridLayout()

        for i in range(6):
            grid.setColumnStretch(i, 1)

        greeting_label = QLabel("Добро пожаловать\nв Систему учета посещений\nBISITOR")
        greeting_label.setWordWrap(True)
        greeting_label.setAlignment(Qt.AlignCenter)
        grid.addWidget(greeting_label, 0, 1, 1, 4)

        login_label = QLabel("Логин")
        login_label.setAlignment(Qt.AlignRight)
        grid.addWidget(login_label, 1, 0, 1, 1)

        self.login_input = QLoginInput()
        grid.addWidget(self.login_input, 1, 1, 1, 5)

        password_label = QLabel("Пароль")
        password_label.setAlignment(Qt.AlignRight)
        grid.addWidget(password_label, 2, 0, 1, 1)

        self.password_input = QLineEdit()
        self.password_input.setEchoMode(QLineEdit.Password)
        grid.addWidget(self.password_input, 2, 1, 1, 5)

        self.log_in = QPushButton("Войти")
        self.log_in.clicked.connect(self.auth)
        grid.addWidget(self.log_in, 3, 1, 1, 4)

        self.sign_in = QPushButton("Зарегистрироваться")
        self.sign_in.clicked.connect(self.show_form)
        grid.addWidget(self.sign_in, 4, 1, 1, 4)

        self.setLayout(grid)

        self.setFixedSize(QSize(400, 250))
        self.setGeometry(QStyle.alignedRect(Qt.LeftToRight, Qt.AlignCenter, self.size(), QApplication.desktop().availableGeometry()))

        self.setWindowTitle('СПбГУТ - Система учета посещаемости')

        self.auth_success.connect(self.on_auth_success)

    # signals
    auth_success = pyqtSignal('PyQt_PyObject')

    # slots
    @pyqtSlot('PyQt_PyObject')
    def on_auth_success(self, auth):
        from DataBase2 import Auth
        from Client.Debug.WrongId import debug
        auth = Auth.log_in(**auth)
        professor = auth.user

        SettingsAPI.synch(professor)

        Settings.load(professor)
        debug(auth.user)
        # не смотря на то, что окно аутентификации больше не нужно, создав локальную переменную,
        # мы заставим сборщик мусора удалить python wrapper of MainWindow поле выхода из функции,
        # что поломает почти всё
        self.window = MainWindow(professor=professor)
        self.window.show()

        self.close()

    def auth(self, *args):
        def on_error(msg):
            raise BisitorException(msg)

        from DataBase2 import Auth
        from Client.MyQt.Widgets.Network.Request import RequestWidget

        login = self.login_input.login()
        password = self.password_input.text()
        if login == '' or password == '':
            Message().information(self, 'Вход в систему', 'Укажите логин и пароль.')
        else:
            try:
                a = Auth.log_in(login, password)

                self.auth_success.emit(dict(login=login, password=password))
            except InvalidLoginException:
                self.loading = FirstLoad.load(Auth(login=login, password=password), self.auth, )

    def keyPressEvent(self, a0: QtGui.QKeyEvent):
        if a0.key() + 1 == QtCore.Qt.Key_Enter:
            self.auth()

    def show_form(self):
        from Client.MyQt.Widgets.NewUserForm import NewUserForm
        if self.new_user_form is None:
            self.new_user_form = NewUserForm()

        self.new_user_form.show()
