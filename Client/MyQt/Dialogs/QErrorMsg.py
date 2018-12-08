from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QErrorMessage

from Client.MyQt.Window.interfaces import IChildWindow


class QErrorMsg(QErrorMessage, IChildWindow):
    """
    TODO: не закрывается
    """

    def __init__(self, *args, msg):
        QErrorMessage.__init__(self, *args)
        IChildWindow.__init__(self)
        self.setAttribute(Qt.WA_DeleteOnClose, True)

        self.msg = msg

    def showAsChild(self, *args):
        self.showMessage(self.msg)

    def closeEvent(self, QCloseEvent):
        self.closeSelf()
        QErrorMessage.closeEvent(self, QCloseEvent)

    def done(self, p_int):
        self.closeSelf()
