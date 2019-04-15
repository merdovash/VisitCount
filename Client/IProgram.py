from Client.MyQt.Window import AbstractWindow
from Client.Reader.SerialReader import RFIDReader
from DataBase2 import Auth as Authentication


class IProgram:
    window: AbstractWindow

    def __getitem__(self, item):
        raise NotImplementedError()

    def __setitem__(self, key, value):
        raise NotImplementedError()

    def reader(self) -> RFIDReader:
        raise NotImplementedError()

    def change_user(self):
        raise NotImplementedError()

    def auth_success(self, auth: Authentication):
        raise NotImplementedError()
