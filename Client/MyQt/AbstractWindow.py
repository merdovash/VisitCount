import traceback

from PyQt5.QtCore import pyqtSlot, pyqtSignal
from PyQt5.QtWidgets import QMainWindow, QErrorMessage

from Client.MyQt.Window.Chart.QAnalysisDialog import QAnalysisDialog
from Client.test import safe


# TODO replace MyProgram with AbstractWindow

class AbstractWindow(QMainWindow):
    error = pyqtSignal(str)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.error.connect(self.on_error)

    @safe
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
    @safe
    def on_error(self, msg):
        # print("hello")
        # print(threading.current_thread().name)
        self.dialog = QErrorMessage(self)
        self.dialog.showMessage(msg)


    def change_widget(self, widget):
        self.setCentralWidget(widget)
