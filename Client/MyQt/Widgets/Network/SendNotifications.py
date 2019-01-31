from PyQt5.QtWidgets import QMessageBox

from Client.MyQt.Widgets.Network.Request import RequestWidget
from DataBase2 import Professor
from Modules import Notification
from Modules.Notification.ClientSide import NotificationSender


class SendNotifications(RequestWidget):
    def __init__(self, host: str, professor: Professor or None, parent=None):
        super().__init__(
            address=host + Notification.address,
            parent=parent,
            worker=NotificationSender(professor, host)
        )

        self.worker.finish.connect(self.show_result)

    def show_result(self, data):
        QMessageBox().information(self, "Отчет о рассылке", data)
