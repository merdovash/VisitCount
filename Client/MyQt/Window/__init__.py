from PyQt5.QtCore import pyqtSlot, pyqtSignal
from PyQt5.QtWidgets import QMainWindow

from Client.MyQt.Dialogs.ErrorMessage import ErrorMessage
from Client.MyQt.Dialogs.OkMessage import OkMessage
from Client.MyQt.Window.interfaces import IParentWindow


class AbstractWindow(QMainWindow, IParentWindow):
    error = pyqtSignal(str)
    message = pyqtSignal(str, bool)
    ok_message = pyqtSignal(str)

    def __init__(self, *args, **kwargs):
        super(QMainWindow, self).__init__()
        super(IParentWindow, self).__init__()

        self.error.connect(self.on_error)
        self.message.connect(self.on_show_message)
        self.ok_message.connect(self.on_ok_message)

    def change_widget(self, widget):
        self.setCentralWidget(widget)

    @pyqtSlot(str)
    def on_error(self, msg):
        self.setDialog(ErrorMessage(self, msg=msg))

    @pyqtSlot(str, bool)
    def on_show_message(self, text, is_red):
        self.centralWidget().show_message(text, is_red)

    @pyqtSlot(str, name='on_ok_message')
    def on_ok_message(self, text):
        self.setDialog(OkMessage(text))
