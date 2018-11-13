"""
This module contains class wrapper of all global variables
"""
import os
from pathlib import PurePath

from Client.Configuartion import WindowConfig
from Client.Configuartion.WindowConfig import Config
from Client.IProgram import IProgram
from Client.MyQt.Window import AbstractWindow
from Client.Reader import IReader
from Client.Reader.SerialReader import RFIDReader, RFIDReaderNotFoundException
from DataBase2 import Session
from Domain import Action


class MyProgram(IProgram):
    __slots__ = ()
    """
    Wrapper of all global variables
    """

    def __init__(self, widget: AbstractWindow = None,
                 win_config: Config = WindowConfig.load(), test=False,
                 css=True):
        self._state = {'marking_visits': False,
                       'host': 'http://bisitor.itut.ru',
                       'date_format': '%Y-%m-%d %H:%M:%f'}

        self._reader: IReader = None

        self.test = test

        self.host = 'http://bisitor.itut.ru'

        self.session = Session()

        self.auth = None

        if css:
            with open(PurePath(os.path.dirname(__file__), 'style.css'), 'r+') as f:
                self.css = f.read()
        else:
            self.css = None

        if widget is None:
            from Client.MyQt.Window.Auth import AuthWindow
            self.window = AuthWindow(self, css=self.css)
        else:
            self.window: AbstractWindow = widget

        self.win_config: WindowConfig = win_config

        self.window.show()

    def set_window(self, widget: AbstractWindow):
        """
        Sets new window as main and only window of program
        :param widget: new window
        """
        self.window.close()
        self.window: AbstractWindow = widget
        self.window.setStyleSheet(self.css)
        self.window.show()

    def reader(self) -> IReader:
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

    def auth_success(self, auth: dict):
        """
        Switch to MainWindow
        :param auth: you have to pass Authentication to switch to MainWindow
        """
        from Client.MyQt.Window.Main import MainWindow
        print('loading MainWindow')
        self.auth = Action.log_in(**auth)
        self.professor = self.auth.user
        self.win_config.set_professor_id(self.auth.user.id)
        self.set_window(MainWindow(program=self, professor=self.professor))
        print("load completed")

    def change_user(self, *args):
        """
        Log out from MainWindow and shows AuthenticationWindow
        """
        from Client.MyQt.Window.Auth import AuthWindow
        self.win_config.log_out()
        self.set_window(AuthWindow(self))

    def __setitem__(self, key, value):
        self._state[key] = value

    def __getitem__(self, item):
        return self._state.get(item, None)
