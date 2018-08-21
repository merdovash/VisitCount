from PyQt5 import QtGui, QtCore
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLineEdit, QFormLayout, QLabel, QPushButton, QDialog, \
    QErrorMessage

from Client.MyQt.AbstractWindow import AbstractWindow
from Client.MyQt.Program import MyProgram
from Client.MyQt.QtMyLoginInput import QLoginInput
from Client.SerialsReader import RFIDReader, RFIDReaderNotFoundException
from Client.test import try_except
from DataBase.Authentication import Authentication
from Modules.FirstLoad.ClientSide import FirstLoad


class AuthWindow(AbstractWindow):
    error = QtCore.pyqtSignal(str)

    def __init__(self, program: MyProgram, flags=None, *args, **kwargs):
        super().__init__(flags, *args, **kwargs)
        self.resize(300, 200)
        self.setCentralWidget(QMyAuthWidget(program))
        self.dialog = None
        self.error.connect(self.on_error)


class QMyAuthWidget(QWidget):
    def __init__(self, program: 'MyProgram', *args, **kwargs):
        super(QMyAuthWidget, self).__init__(*args, **kwargs)
        self.program: 'MyProgram' = program
        self.db = program.db

        self.setup_geometry()
        self.setupUI()
        self.setup_serial()

        self.dialog = None
        pass

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
        self.auth_btn.setStyleSheet(self.db.config.main_button_css)
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

        try:
            RFIDReader.instance().onRead(imaged_value)
        except RFIDReaderNotFoundException:
            pass

    @try_except
    def _first_load(self, auth:Authentication):
        FirstLoad(db=self.db,
                  auth=auth,
                  card_id=self.login_input.card_id(),
                  login=self.login_input.login(),
                  password=self.password_input.text(),
                  program=self.program,
                  on_finish=self.auth).run()

    @try_except
    def auth(self, *args):
        auth = Authentication(self.db, login=self.login_input.login(),
                              password=self.password_input.text(), card_id=self.login_input.card_id())
        if auth.status:
            from Client.MyQt.Window.QtMyMainWindow import MainWindow
            self.program.set_new_window(MainWindow(auth, self.program, self.program.win_config))

        else:
            self._first_load(auth)

    def keyPressEvent(self, a0: QtGui.QKeyEvent):
        print("keypressEvent", a0.key(), QtCore.Qt.Key_Enter)
        if a0.key() + 1 == QtCore.Qt.Key_Enter:
            self.auth()
