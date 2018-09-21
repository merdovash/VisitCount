from PyQt5 import QtGui, QtCore
from PyQt5.QtCore import Qt, pyqtSignal, pyqtSlot
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLineEdit, QFormLayout, QLabel, QPushButton, QDialog, \
    QErrorMessage

from Client.Domain.Authentication import Authentication
from Client.Domain.Exception import NoSuchUserException
from Client.Domain.ServerRequest.FirstLoad import FirstLoad
from Client.IProgram import IProgram
from Client.MyQt.Window import AbstractWindow
from Client.MyQt.Window.Auth.QtMyLoginInput import QLoginInput
from Client.test import safe
# from DataBase.Authentication import Authentication
# from DataBase.ClentDataBase import ClientDataBase
# from Modules.FirstLoad.ClientSide import FirstLoad
from DataBase2 import Auth


class AuthWindow(AbstractWindow):

    def __init__(self, program, flags=None, *args, **kwargs):
        super().__init__(flags, *args, **kwargs)
        self.resize(300, 200)
        self.setCentralWidget(AuthWidget(program))
        self.dialog = None


class AuthWidget(QWidget):
    def __init__(self, program: IProgram, *args, **kwargs):
        super(AuthWidget, self).__init__(*args, **kwargs)
        self.program: IProgram = program

        self.setup_geometry()
        self.setupUI()
        self.setup_serial()

        self.dialog = None

        self.auth_success.connect(self.on_auth_success)
        pass

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

    def setupUI(self):
        self.inner_layout = QVBoxLayout()

        # login input field
        self.login_input = QLoginInput()
        self.login_input.setPlaceholderText("Или приложите карточку к считывателю")

        # password input field
        self.password_input = QLineEdit()
        self.password_input.setEchoMode(QLineEdit.Password)

        form_layout = QFormLayout()

        # header
        header = QLabel("Вход в систему")
        header.setAlignment(Qt.AlignCenter)

        self.auth_btn = QPushButton()
        self.auth_btn.setText("Аутентификация")
        self.auth_btn.setStyleSheet("background-color: #ff8000; color: #ffffff; font-weight: bold;")
        self.auth_btn.clicked.connect(self.auth)

        # add to layouts
        self.inner_layout.addWidget(header, Qt.AlignCenter)
        self.inner_layout.addLayout(form_layout)
        form_layout.addRow(QLabel("Введите Логин"), self.login_input)
        form_layout.addRow(QLabel("Введите Пароль"), self.password_input)
        self.inner_layout.addWidget(self.auth_btn, 2, Qt.AlignBottom)

        self.loading_info = QLabel()
        self.inner_layout.addWidget(self.loading_info, 4, Qt.AlignBottom)

        self.setLayout(self.inner_layout)

    def setup_geometry(self):
        self.resize(350, 200)
        self.setWindowTitle("Аутентификация")

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
