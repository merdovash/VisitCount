from PyQt5.QtCore import pyqtSlot, pyqtSignal
from PyQt5.QtWidgets import QMainWindow, QErrorMessage

from Client.MyQt.Chart import QAnalysisDialog
# TODO replace MyProgram with AbstractWindow
from Client.MyQt.Dialogs.OkMessage import OkMessage


class AbstractWindow(QMainWindow):
    error = pyqtSignal(str)
    message = pyqtSignal(str, bool)
    ok_message = pyqtSignal(str)

    def __init__(self, *args, **kwargs):
        super().__init__()

        self.error.connect(self.on_error)
        self.message.connect(self.on_show_message)
        self.ok_message.connect(self.on_ok_message)

        self.dialog = None

    def setDialog(self, dialog: QAnalysisDialog):
        """

        :param dialog: QAnalysisDialog that contains graph to show
        """
        self.dialog = dialog
        self.dialog.show()

    def showError(self, msg):
        self.dialog = QErrorMessage()
        self.dialog.showMessage(msg)

    @pyqtSlot(str)
    def on_error(self, msg):
        # # print("hello")
        # # print(threading.current_thread().name)
        self.dialog = QErrorMessage(self)
        self.dialog.showMessage(msg)

    @pyqtSlot(str, bool)
    def on_show_message(self, text, is_red):
        self.centralWidget().show_message(text, is_red)

    def change_widget(self, widget):
        self.setCentralWidget(widget)

    @pyqtSlot(str, name='on_ok_message')
    def on_ok_message(self, text):
        self.dialog = OkMessage(text)
        self.dialog.exec_()
