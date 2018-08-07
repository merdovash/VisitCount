import traceback

from DataBase.sql_handler import DataBaseWorker
from PyQt5 import QtGui, QtCore
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLineEdit, QFormLayout, QLabel, QPushButton, QMessageBox, QDialog

from Main import config
from Main.MyQt.QtMyLoginInput import QLoginInput
from Main.Requests.Load import FirstLoad
from Main.SerialsReader import RFIDReader, RFIDReaderNotFoundException


class QMyAuthWidget(QWidget):
    def __init__(self, window: 'MyProgram', *args, **kwargs):
        super(QMyAuthWidget, self).__init__(*args, **kwargs)

        self.window = window

        self.db = DataBaseWorker(config)

        self.setup_geometry()
        self.setupUI()
        self.setup_serial()

        self.dialog = None
        pass

    def showDialog(self, d:QDialog):
        self.dialog = d
        self.dialog.show()

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
        self.auth_btn.setStyleSheet(config.main_button_css)
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
            RFIDReader.instance().onRead = imaged_value
        except RFIDReaderNotFoundException:
            pass

    def _auth(self)->(DataBaseWorker.AuthStatus, int):
        status = DataBaseWorker.AuthStatus.Fail
        if self.login_input.image:
            print("by card")
            status, professor_id = self.db.auth(
                card_id=self.login_input.text(),
                password=self.password_input.text())
        else:
            try:
                status, professor_id = self.db.auth(
                    login=self.login_input.text(),
                    password=self.password_input.text())
            except Exception:
                traceback.print_exc()

        return status, professor_id

    def _first_load(self):
        try:
            if self.login_input.image:
                print("FIRST LOAD by card")
                FirstLoad(card_id=self.login_input.text(),
                          password=self.password_input.text(),
                          parent=self,
                          on_finish=self.auth).run()
            else:
                FirstLoad(login=self.login_input.text(),
                          password=self.password_input.text(),
                          parent=self,
                          on_finish=self.auth).run()
        except Exception as e:
            traceback.print_exc()

    def auth(self):
        status, professor_id = self._auth()
        print(status)

        if status == DataBaseWorker.AuthStatus.Success:
            self._auth_success_event(professor_id)

        elif status == DataBaseWorker.AuthStatus.NoData:
            print("start FIRST LOAD")
            self._first_load()

        elif status == DataBaseWorker.AuthStatus.Fail:
            self.msg = QMessageBox()
            self.msg.setText("Неверная комбинация логина и пароля")
            self.msg.show()

    def _auth_success_event(self, professor_id):
        self.window.auth_success(professor_id)

    def keyPressEvent(self, a0: QtGui.QKeyEvent):
        print("keypressEvent", a0.key(), QtCore.Qt.Key_Enter)
        if a0.key() + 1 == QtCore.Qt.Key_Enter:
            self.auth()