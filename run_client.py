import os
import sys
import traceback

import PyQt5
from PyQt5 import QtWidgets
from PyQt5.QtWidgets import *

from Client.Configuartion import WindowConfig
from Client.IProgram import IProgram
from Client.Program import MyProgram

pyqt = os.path.dirname(PyQt5.__file__)
QApplication.addLibraryPath(os.path.join(pyqt, "plugins"))

print(os.path.dirname(__file__))


if __name__ == "__main__":
    old_hook = sys.excepthook


    def catch_exceptions(t, val, tb):
        QtWidgets.QMessageBox.critical(None,
                                       "An exception was raised",
                                       "Exception type: {},\n"
                                       "value: {},\n"
                                       "tb: {}".format(t, val, traceback.format_tb(tb)))
        old_hook(t, val, tb)


    sys.excepthook = catch_exceptions

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

    # test(program)

    sys.exit(app.exec_())
