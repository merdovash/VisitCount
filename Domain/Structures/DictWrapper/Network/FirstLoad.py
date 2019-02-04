from typing import Dict

from DataBase2 import UserType
from Domain.Structures.DictWrapper import Structure
from Domain.Structures.DictWrapper.Network import TablesData


class ClientFirstLoadData(Structure):
    login: str
    password: str
    type: int

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

