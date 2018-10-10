import os
import sys

import PyQt5
from PyQt5 import QtWidgets
from PyQt5.QtWidgets import *

from Client.Configuartion import WindowConfig
from Client.IProgram import IProgram
from Client.Program import MyProgram

pyqt = os.path.dirname(PyQt5.__file__)
QApplication.addLibraryPath(os.path.join(pyqt, "plugins"))

print(os.path.dirname(__file__))


def check_modules():
    try:
        from pip import main as _main

    except:
        from pip._internal import main as _main

    try:
        import PyQt5
    except:
        _main(['install', 'pyqt5'])

    try:
        import serial
    except:
        _main(['install', 'pyqt5'])

    try:
        import pymysql
    except:
        _main(['install', 'pymysql'])

    try:
        import sqlite3
    except:
        _main(['install', 'sqlite3'])

    try:
        import matplotlib
    except:
        _main(['install', 'matplotlib'])

    try:
        import numpy
    except:
        _main(['install', 'numpy'])

    try:
        import json
    except:
        _main(['install', 'json'])

    try:
        import requests
    except:
        _main(['install', 'requests'])


if __name__ == "__main__":
    window_config = WindowConfig.load()
    if window_config['modules'] != True:
        check_modules()
        window_config['modules'] = True
        window_config.sync()

    kwargs = {}

    if 'test' in sys.argv:
        kwargs['test'] = True

    app = QApplication(sys.argv)
    app.setStyle(QtWidgets.QStyleFactory.create('Fusion'))
    app.setApplicationName("СПбГУТ - Учет посещений")

    program: IProgram = MyProgram(win_config=window_config, **kwargs)

    sys.exit(app.exec_())
