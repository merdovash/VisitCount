from typing import Dict

from DataBase2 import Auth, UserType
from Domain.Structures.DictWrapper import Structure
from Domain.Structures.DictWrapper.Network import TablesData


class ClientFirstLoadData(Structure):
    login: str
    password: str
    type: UserType

    def __init__(self, login, password, type=UserType.PROFESSOR):
        self.login = login
        self.password = password
        self.type = type


class ServerFirstLoadData(Structure):
    professor: Dict
    auth: Dict

    data: TablesData

    def __init__(self, **kwargs):
        if 'auth' in kwargs.keys():
            self.auth = kwargs.pop('auth')
        elif 'Auth' in kwargs.keys():
            self.auth = kwargs.pop('Auth')
        else:
            raise ValueError('auth is required')

        if isinstance(self.auth, Auth):
            self.auth = {key: Auth.column_type(key)(value) for key, value in self.auth.dict().items()}
        else:
            self.auth = {key: Auth.column_type(key)(value) for key, value in self.auth.items()}

        if 'professor' in kwargs:
            self.professor = kwargs.pop('professor')
        elif 'Professor' in kwargs:
            self.professor = kwargs.pop('Professor')
        else:
            raise ValueError('professor is required')

        if 'data' in kwargs:
            self.data = TablesData(kwargs.get('data'))
        else:
            self.data = kwargs

