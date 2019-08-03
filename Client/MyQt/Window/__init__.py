import traceback

from PyQt5.QtCore import pyqtSlot, pyqtSignal
from PyQt5.QtWidgets import QMainWindow, QMessageBox

from Domain.Exception import BisitorException


class AbstractWindow(QMainWindow):
    error = pyqtSignal('PyQt_PyObject', 'PyQt_PyObject', 'PyQt_PyObject')
    message = pyqtSignal(str, bool)
    ok_message = pyqtSignal(str)

    def __init__(self, *args, **kwargs):
        super(QMainWindow, self).__init__()

        if 'css' in kwargs:
            with open(kwargs['css'], 'r') as style:
                self.setStyleSheet(style.read())

        self.error.connect(self.on_error)
        self.message.connect(self.on_show_message)
        self.ok_message.connect(self.on_ok_message)

    def change_widget(self, widget):
        self.setCentralWidget(widget)

    @pyqtSlot('PyQt_PyObject', 'PyQt_PyObject', 'PyQt_PyObject', name='on_error')
    def on_error(self, exception_type, exception, tb):
        if isinstance(exception, BisitorException):
                exception.show(self)
        else:
            QMessageBox().critical(self,
                                   "Непредвиденная ошибка",
                                   "Exception type: {},\n"
                                   "value: {},\n"
                                   "tb: {}".format(exception_type, exception, traceback.format_tb(tb)))

    @pyqtSlot(str, bool)
    def on_show_message(self, text, is_red):
        self.central_widget.show_message(text, is_red)

    @pyqtSlot(str, name='on_ok_message')
    def on_ok_message(self, text):
        QMessageBox().information(self, "Сообщение", text)

