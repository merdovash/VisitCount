from Client.Domain.Exception import NoSuchUserException
from DataBase2 import auth


def Authentication(**kwargs):
    authentication = auth.Authentication(**kwargs)

    if authentication is None:
        raise NoSuchUserException()

    return authentication


def host():
    return 'http://bisitor.itut.ru'
