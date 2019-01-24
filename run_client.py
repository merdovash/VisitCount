import os
import sys
import traceback

import PyQt5
from PyQt5.QtCore import QThread
from PyQt5.QtWidgets import QMessageBox, QApplication

from Client.Configuartion import WindowConfig
from Client.IProgram import IProgram
from Client.Program import MyProgram
from Domain.Exception import BisitorException

pyqt = os.path.dirname(PyQt5.__file__)
QApplication.addLibraryPath(os.path.join(pyqt, "plugins"))

print(os.path.dirname(__file__))

if __name__ == "__main__":
    window_config = WindowConfig.load()

    kwargs = {}

    if 'test' in sys.argv:
        kwargs['test'] = True

    if 'no-css' in sys.argv:
        kwargs['css'] = False

    if '-host' in sys.argv:
        kwargs['host'] = sys.argv[sys.argv.index('-host') + 1]
    elif '-H' in sys.argv:
        kwargs['host'] = sys.argv[sys.argv.index('-H') + 1]

    app = QApplication(sys.argv)
    # app.setStyle(QtWidgets.QStyleFactory.create('Fusion'))
    app.setApplicationName("СПбГУТ - Учет посещений")

    program: IProgram = MyProgram(win_config=window_config, **kwargs)

    old_hook = sys.excepthook


    def catch_exceptions(exception_type, exception, tb):
        program.window.error.emit(exception_type, exception, tb)
        old_hook(exception_type, exception, tb)


    sys.excepthook = catch_exceptions

    # test(program)

    sys.exit(app.exec_())
