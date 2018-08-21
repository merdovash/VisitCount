import traceback

from PyQt5.QtCore import pyqtSlot
from PyQt5.QtWidgets import QMainWindow, QErrorMessage

from Client.MyQt.Window.Chart.QAnalysisDialog import QAnalysisDialog
from Client.test import safe


# TODO replace MyProgram with AbstractWindow

class AbstractWindow(QMainWindow):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

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
    def on_error(self, msg):
        try:
            # print("hello")
            # print(threading.current_thread().name)
            self.dialog = QErrorMessage(self)
            self.dialog.showMessage(msg)
        except Exception:
            traceback.print_exc()

    def change_widget(self, widget):
        self.setCentralWidget(widget)
