import warnings

from DataBase2 import Session


class IDataBaseUser:
    def __init__(self, session=None):
        if session is None:
            self.session = Session()
        else:
            self.session = Session()
