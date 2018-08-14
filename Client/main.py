import os
import sys
from PyQt5 import QtCore

import PyQt5
from PyQt5.QtWidgets import *

from Client.Configuartion import WindowConfig
from Client.Configuartion.WindowConfig import Config
from Client.MyQt.AuthWindow import QMyAuthWidget, AuthWindow
from Client.MyQt.Window.QtMyMainWindow import MainWindow
from Client.test import try_except
from DataBase.Authentication import Authentication
from DataBase.sql_handler import ClientDataBase
from config2 import DataBaseConfig

pyqt = os.path.dirname(PyQt5.__file__)
QApplication.addLibraryPath(os.path.join(pyqt, "plugins"))

print(os.path.dirname(__file__))


class MyProgram:
    def __init__(self, widget=None, win_config: Config = None):
        self.state = {'marking_visits': False}

        db_config = DataBaseConfig()
        self.db = ClientDataBase(db_config)
        if widget is None:
            self.window: QMainWindow = AuthWindow(self, flags=None)
        else:
            self.window = widget

        if win_config is not None:
            self.win_config = win_config
        else:
            self.win_config = WindowConfig.load()

        self.window.show()

    @try_except
    def set_new_window(self, widget):
        self.window.close()
        self.window = widget
        self.window.show()

    @try_except
    def auth_success(self, auth: Authentication):
        self.set_new_window(MainWindow(auth=auth, program=self, window_config=self.win_config))

    def change_user(self):
        self.set_new_window(QMyAuthWidget(self, self.db))

    def __setitem__(self, key, value):
        self.state[key] = value

    def __getitem__(self, item):
        return self.state[item]


if __name__ == "__main__":
    app = QApplication(sys.argv)
    os.environ["QT_QUICK_CONTROLS_STYLE"] = "Material"
    app.setApplicationName("СПбГУТ - Учет посещений")

    program = MyProgram()

    sys.exit(app.exec_())
