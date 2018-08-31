# TODO
from Client.Reader.SerialReader import RFIDReader
from DataBase.Authentication import Authentication
from DataBase.ClentDataBase import ClientDataBase


class IProgram:
    __slots__ = ('window', 'win_config', '_reader', '_state', '_database', 'auth')

    def __getitem__(self, item):
        raise NotImplementedError()

    def __setitem__(self, key, value):
        raise NotImplementedError()

    def reader(self) -> RFIDReader:
        raise NotImplementedError()

    def database(self) -> ClientDataBase:
        raise NotImplementedError

    def change_user(self):
        raise NotImplementedError()

    def auth_success(self, auth: Authentication):
        raise NotImplementedError()
