import os
import sys

import PyQt5
from PyQt5.QtWidgets import *

from Main.Configuartion import WindowConfig
from Main.Configuartion.WindowConfig import Config
from Main.MyQt.AuthWindow import QMyAuthWidget
from Main.MyQt.Window.QtMyMainWindow import MainWindow

pyqt = os.path.dirname(PyQt5.__file__)
QApplication.addLibraryPath(os.path.join(pyqt, "plugins"))

print(os.path.dirname(__file__))


class MyProgram:
    def __init__(self, widget=None, config: Config = None, config_path: str = None):
        if widget is None:
            self.window = QMyAuthWidget(self)
        else:
            self.window = widget

        if config is not None:
            self.conf = config
        elif config_path is not None:
            self.conf = WindowConfig.load(config_path)
        else:
            self.conf = WindowConfig.load()

        self.window.show()

    def set_new_window(self, widget):
        self.window.close()
        self.window = widget
        self.window.show()

    def auth_success(self, professor_id):
        self.set_new_window(MainWindow(professor_id, self, self.conf))

    def change_user(self):
        self.set_new_window(QMyAuthWidget(self))


if __name__ == "__main__":
    app = QApplication(sys.argv)
    os.environ["QT_QUICK_CONTROLS_STYLE"] = "Material"
    app.setApplicationName("СПбГУТ - Учет посещений")

    program = MyProgram()

    sys.exit(app.exec_())
