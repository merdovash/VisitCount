import argparse
import os
import sys

import PyQt5
from PyQt5.QtGui import QFont
from PyQt5.QtWidgets import QApplication, QStyleFactory

from Client.IProgram import IProgram
from Client.Program import MyProgram
from Parser.client import client_args

pyqt = os.path.dirname(PyQt5.__file__)
QApplication.addLibraryPath(os.path.join(pyqt, "plugins"))

if __name__ == "__main__":
    app = QApplication(sys.argv)
    font = QFont('Roboto')
    font.setPixelSize(12)
    font.setStyleName('Regular')
    app.setFont(font)
    app.setStyle(QStyleFactory().create('Fusion'))
    app.setApplicationName("СПбГУТ - Учет посещений")

    print(client_args)
    program: IProgram = MyProgram(css=client_args.css, test=client_args.test, host=client_args.host)

    old_hook = sys.excepthook

    def catch_exceptions(exception_type, exception, tb):
        program.window.error.emit(exception_type, exception, tb)
        old_hook(exception_type, exception, tb)

    sys.excepthook = catch_exceptions

    # test(program)

    sys.exit(app.exec_())
