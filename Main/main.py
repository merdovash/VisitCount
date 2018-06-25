import sys
from PyQt5 import QtCore

from PyQt5.QtCore import pyqtSlot, Qt
from qtpy import QtGui

from Main import SerialsReader, sql_handler, config

from PyQt5.QtWidgets import *

from Main.Load import FirstLoad
from Main.MyQt.QtMyLoginInput import QLoginInput
from Main.MyQt.QtMyMainWindow import QMyMainWindow


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
        layout = QVBoxLayout()

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
        layout.addWidget(header)
        layout.addLayout(form_layout)
        form_layout.addRow(QLabel("Введите Логин"), self.login_input)
        form_layout.addRow(QLabel("Введите Пароль"), self.password_input)
        layout.addWidget(self.auth_btn)

        self.setLayout(layout)

    def setup_geometry(self):
        self.resize(350, 200)
        self.setWindowTitle("Аутентификация")

    def setup_serial(self):
        def imaged_value(prof_id):
            print(int(prof_id))
            prof = self.db.get_professors(card_id=int(prof_id))[0]
            name = prof['last_name'] + ' ' + prof['first_name'] + ' ' + prof['middle_name']
            self.login_input.set_image_text(prof_id, name)

        self.window.serial.method = imaged_value
        self.window.serial.start()

    @pyqtSlot()
    def auth(self):
        res = self.db.auth(card_id=self.login_input.text(), password=self.password_input.text())
        if len(res) > 0:
            try:
                self.window.set_new_window(QMyMainWindow(res[0]["user_id"], self.window))
            except Exception as e:
                print(e)
        else:
            r = FirstLoad(
                card_id=self.login_input.text(),
                password=self.password_input.text(),
                db=self.db).run()
            if r:
                self.auth()
            else:
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
