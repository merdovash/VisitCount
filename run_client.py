import argparse
import os
import sys

import PyQt5
from PyQt5.QtWidgets import QApplication, QStyleFactory

from Client.IProgram import IProgram
from Client.Program import MyProgram

pyqt = os.path.dirname(PyQt5.__file__)
QApplication.addLibraryPath(os.path.join(pyqt, "plugins"))

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Process parameters")
    parser.add_argument('--host', metavar='H', default='bisitor.itut.ru:50000', type=str, help='you can specify server host address')
    parser.add_argument('--test', type=bool, default=False, help='for testing without Reader')
    parser.add_argument('--css', type=bool, default=True, help='you can disable css')

    args = parser.parse_args()

    app = QApplication(sys.argv)
    app.setStyle(QStyleFactory().create('Fusion'))
    app.setApplicationName("СПбГУТ - Учет посещений")

    program: IProgram = MyProgram(css=args.css, test=args.test, host=args.host)

    old_hook = sys.excepthook

    def catch_exceptions(exception_type, exception, tb):
        program.window.error.emit(exception_type, exception, tb)
        old_hook(exception_type, exception, tb)

    sys.excepthook = catch_exceptions

    # test(program)

    sys.exit(app.exec_())
