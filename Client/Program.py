"""
This module contains class wrapper of all global variables
"""
import os
from pathlib import PurePath

from PyQt5.QtCore import QObject

from Client.IProgram import IProgram
from Client.MyQt.Window import AbstractWindow
from Client.MyQt.Window.Main import MainWindow
from Client.Reader import IReader
from Client.Reader.SerialReader import RFIDReader, RFIDReaderNotFoundException
from Client.src import src
from DataBase2 import Session, Auth
from Debug.WrongId import debug
from Domain.functools.Url import to_standart_http


class MyProgram(IProgram, QObject):
    """
    Wrapper of all global variables
    """

    def __init__(self, widget: AbstractWindow = None, test=False, css: str = src.qss, host='http://bisitor.itut.ru'):
        super().__init__()
        self._state = {'marking_visits': False,
                       'host': 'http://bisitor.itut.ru',
                       'date_format': '%Y-%m-%d %H:%M:%S'}

        self._reader: IReader = None

        self.test = test

        self.host = to_standart_http(host)

        self.session = Session()

        self.auth = None

        self.css = css

        if widget is None:
            from Client.MyQt.Window.Auth import AuthWindow
            self.window = AuthWindow(self, css=self.css)
        else:
            self.window: AbstractWindow = widget

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
        # OnRead.prepare(self, self.window.central_widget.table, self.session)

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
        self.auth = Auth.log_in(**auth)
        self.professor = self.auth.user
        debug(self.auth.user)
        self.set_window(MainWindow(program=self, professor=self.professor))

    def change_user(self, *args):
        """
        Log out from MainWindow and shows AuthenticationWindow
        """
        from Client.MyQt.Window.Auth import AuthWindow
        self.set_window(AuthWindow(self, css=self.css))
