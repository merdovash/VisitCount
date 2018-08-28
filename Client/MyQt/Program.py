"""
This module contains class wrapper of all global variables
"""

from Client.Configuartion import WindowConfig
from Client.Configuartion.WindowConfig import Config
from Client.MyQt.Window import AbstractWindow
from Client.Reader import RFIDReaderNotFoundException, RFIDReader
from Client.test import safe
from DataBase.Authentication import Authentication
from DataBase.ClentDataBase import ClientDataBase


class MyProgram:
    # __slots__ = ('db', 'window', 'win_config', 'auth', '_state', '_reader', 'change_user')
    """
    Wrapper of all global variables
    """

    def __init__(self, widget: AbstractWindow = None,
                 win_config: Config = WindowConfig.load('Client/window_config.json')):
        self._state = {'marking_visits': False,
                       'host': 'http://bisitor.itut.ru',
                       'date_format': '%Y-%m-%d %H:%M:%f'}

        self.db = ClientDataBase()

        self._reader = None

        if widget is None:
            from Client.MyQt.Window.Auth import AuthWindow
            self.window = AuthWindow(self)
        else:
            self.window: AbstractWindow = widget

        self.win_config: WindowConfig = win_config

        self.window.show()

        self.auth = None

    @safe
    def set_window(self, widget: AbstractWindow):
        """
        Sets new window as main and only window of program
        :param widget: new window
        """
        self.window.close()
        self.window: AbstractWindow = widget
        self.window.show()

    @safe
    def reader(self) -> RFIDReader:
        """
        Returns RFIDReader if its connected.
        Saves RFIDReader instance in private variable.
        :return:
        """
        if self._reader is None:
            try:
                self._reader = RFIDReader.instance()
            except RFIDReaderNotFoundException:
                self._reader = None
        return self._reader

    @safe
    def auth_success(self, auth: Authentication):
        """
        Switch to MainWindow
        :param auth: you have to pass Authentication to switch to MainWindow
        """
        from Client.MyQt.Window.Main import MainWindow
        self.auth = auth
        self._state['professor_id'] = auth.user_id
        self.win_config.set_professor_id(auth.user_id)
        self.set_window(MainWindow(program=self))

    @safe
    def change_user(self, *args):
        """
        Log out from MainWindow and shows AuthenticationWindow
        """
        from Client.MyQt.Window.Auth import AuthWindow
        self.win_config.log_out()
        self.set_window(AuthWindow(self))

    @safe
    def __setitem__(self, key, value):
        self._state[key] = value

    @safe
    def __getitem__(self, item):
        return self._state[item]
