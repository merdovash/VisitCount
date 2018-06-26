import sys
from PyQt5 import QtCore

from PyQt5.QtCore import pyqtSlot, Qt
from qtpy import QtGui

from Main import SerialsReader, sql_handler, config

from PyQt5.QtWidgets import *

from Main.Load import FirstLoad
from Main.MyQt.QtMyDownloadingWidget import QLoadingWidget
from Main.MyQt.QtMyLoginInput import QLoginInput
from Main.MyQt.QtMyMainWindow import QMyMainWindow
from Main.sql_handler import DataBaseWorker


class MyProgram:
    def __init__(self):
        self.serial = SerialsReader.SerialThread(None)

        self.window = QMyAuthWidget(self)

        self.window.show()

    def set_new_window(self, widget):
        self.window.close()
        self.window = widget
        self.window.show()


class QMyAuthWidget(QWidget):
    def __init__(self, window: MyProgram, *args, **kwargs):
        super(QMyAuthWidget, self).__init__(*args, **kwargs)

        self.window = window

        self.db = sql_handler.DataBaseWorker()

        self.setup_geometry()
        self.setupUI()
        self.setup_serial()
        pass

    def setupUI(self):
        self.l = QVBoxLayout()

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
        self.l.addWidget(header)
        self.l.addLayout(form_layout)
        form_layout.addRow(QLabel("Введите Логин"), self.login_input)
        form_layout.addRow(QLabel("Введите Пароль"), self.password_input)
        self.l.addWidget(self.auth_btn)

        self.setLayout(self.l)

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
                name = prof['last_name'] + ' ' + prof['first_name'] + ' ' + prof['middle_name']
                self.login_input.set_image_text(prof_card_id, name)

        self.window.serial.method = imaged_value
        self.window.serial.start()

    @pyqtSlot()
    def auth(self):
        status, professor_id = self.db.auth(card_id=self.login_input.text(), password=self.password_input.text())
        if status == DataBaseWorker.AuthStatus.Success:
            try:
                self.window.set_new_window(QMyMainWindow(professor_id, self.window))
            except Exception as e:
                print(e)
        elif status == DataBaseWorker.AuthStatus.NoData:
            self.status = QLoadingWidget()
            self.l.addWidget(self.status)

            try:
                FirstLoad(
                    card_id=self.login_input.text(),
                    password=self.password_input.text(),
                    db=self.db,
                    data_totals=lambda x: self.status.setTotals(x),
                    data_placer=lambda x: self.status.setMarker(x),
                    on_finish=self.auth).run()
            except Exception as e:
                print("ERROR FirstLoad->", e)
        elif status == DataBaseWorker.AuthStatus.Fail:
            self.msg = QMessageBox()
            self.msg.setText("Неверная комбинация логина и пароля")
            self.msg.show()

    def keyPressEvent(self, a0: QtGui.QKeyEvent):
        print("keypressEvent", a0.key(), QtCore.Qt.Key_Enter)
        if a0.key() + 1 == QtCore.Qt.Key_Enter:
            self.auth()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setApplicationName("СПбГУТ - Учет посещений")

    program = MyProgram()

    sys.exit(app.exec_())
