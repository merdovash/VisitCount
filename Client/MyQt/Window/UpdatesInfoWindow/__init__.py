from PyQt5.QtWidgets import QWidget

from Client.MyQt.Window.UpdatesInfoWindow.Ui_UpdatesInfoWidget import Ui_UpdatesInfoWidget
from Client.MyQt.Window.interfaces import IChildWindow
from DataBase2 import UpdateType


class UpdatesInfoWidget(QWidget, Ui_UpdatesInfoWidget, IChildWindow):
    def __init__(self, updates, flags=None, *args, **kwargs):
        QWidget.__init__(self, flags, *args, **kwargs)
        Ui_UpdatesInfoWidget.setupUi(self, self)
        IChildWindow.__init__(self)

        for update in updates:
            self.table.insertRowData({
                'table': update.table_name,
                'id': str(update.row_id),
                'type': UpdateType.of(update.update_type),
                'date': str(update.date)
            })

        self.setMinimumWidth(self.table.width())

    def showAsChild(self, *args):
        self.show()

    def closeEvent(self, QCloseEvent):
        self.closeSelf()
        QWidget.closeEvent(self, QCloseEvent)
