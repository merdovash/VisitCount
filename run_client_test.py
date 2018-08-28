import os
import sys

import PyQt5
from Client.MyQt.Window.MainWindow import Window
from PyQt5.QtWidgets import *

pyqt = os.path.dirname(PyQt5.__file__)
QApplication.addLibraryPath(os.path.join(pyqt, "plugins"))

print(os.path.dirname(__file__))

if __name__ == "__main__":
    app = QApplication(sys.argv)
    os.environ["QT_QUICK_CONTROLS_STYLE"] = "Material"
    app.setApplicationName("СПбГУТ - Учет посещений")

    program = Window()
    program.show()

    sys.exit(app.exec_())
