from PyQt5.QtWidgets import QDialog

from Client.MyQt.Window.NotificationParam.UiDesign import Ui_NotificationWindow


class NotificationWindow(QDialog, Ui_NotificationWindow):
    def __init__(self, flags, *args, **kwargs):
        super().__init__(flags, *args, **kwargs)

        self.setupUi(self)

        self.new_user_save_btn.clicked.connect(self.on_add_user)

    def on_add_user(self):
        pass
