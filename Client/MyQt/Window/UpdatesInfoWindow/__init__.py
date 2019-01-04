from PyQt5.QtWidgets import QWidget, QTabWidget, QListWidget, QVBoxLayout

from Client.MyQt.Window.UpdatesInfoWindow.Ui_UpdatesInfoWidget import Ui_UpdatesInfoWidget
from Client.MyQt.Window.interfaces import IChildWindow


class UpdatesInfoWidget(QWidget, Ui_UpdatesInfoWidget, IChildWindow):
    def __init__(self, updates, flags=None, *args, **kwargs):
        QWidget.__init__(self, flags, *args, **kwargs)
        Ui_UpdatesInfoWidget.setupUi(self, self)
        IChildWindow.__init__(self)

        self.tabs = QTabWidget()
        for case in updates:
            list_widget = QListWidget()
            list_widget.addItems(updates[case])

            self.tabs.addTab(list_widget, case)

        self.layout_ = QVBoxLayout()
        self.layout_.addWidget(self.tabs)
        self.setLayout(self.layout_)

    def showAsChild(self, *args):
        self.show()

    def closeEvent(self, QCloseEvent):
        self.closeSelf()
        QWidget.closeEvent(self, QCloseEvent)
