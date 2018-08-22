from Client.Configuartion import WindowConfig
from Client.Configuartion.WindowConfig import Config
from Client.MyQt.AbstractWindow import AbstractWindow
from Client.SerialsReader import RFIDReaderNotFoundException, RFIDReader
from Client.test import safe
from DataBase.Authentication import Authentication
from DataBase.config2 import DataBaseConfig
from DataBase.sql_handler import ClientDataBase


class MyProgram:
    def __init__(self, widget: AbstractWindow=None, win_config: Config = WindowConfig.load()):
        self.state = {'marking_visits': False,
                      'host': 'http://bisitor.itut.ru'}

        db_config = DataBaseConfig()
        self.db = ClientDataBase(db_config)

        self._reader = None

        if widget is None:
            from Client.MyQt.AuthWindow import AuthWindow
            self.window: AbstractWindow = AuthWindow(self, flags=None)
        else:
            self.window: AbstractWindow = widget

        self.win_config = win_config

        self.window.show()

    @safe
    def set_new_window(self, widget):
        self.window.close()
        self.window = widget
        self.window.show()

    @safe
    def reader(self):
        if self._reader is None:
            try:
                self._reader = RFIDReader.instance()
            except RFIDReaderNotFoundException:
                self._reader = None
        return self._reader

    @safe
    def auth_success(self, auth: Authentication):
        from Client.MyQt.Window.QtMyMainWindow import MainWindow
        self.set_new_window(MainWindow(auth=auth, program=self, window_config=self.win_config))

    @safe
    def change_user(self, *args):
        from Client.MyQt.AuthWindow import AuthWindow
        self.set_new_window(AuthWindow(self))

    def __setitem__(self, key, value):
        self.state[key] = value

    def __getitem__(self, item):
        return self.state[item]