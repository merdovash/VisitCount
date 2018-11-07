from PyQt5.QtWidgets import QErrorMessage

from Client.MyQt.Window.interfaces import IChildWindow


class ErrorMessage(QErrorMessage, IChildWindow):
    def __init__(self, *args, msg):
        super(QErrorMessage, self).__init__(*args)
        super(IChildWindow, self).__init__()
        self.msg = msg

    def showAsChild(self, *args):
        self.showMessage(self.msg)

    def closeEvent(self, QCloseEvent):
        self.closeSelf()

    def done(self, p_int):
        self.closeSelf()
