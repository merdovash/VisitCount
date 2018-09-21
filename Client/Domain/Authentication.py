from Client.Domain.Exception import NoSuchUserException
from DataBase2 import Auth


def Authentication(**kwargs) -> Auth:
    authentication = Auth.log_in(**kwargs)

    if authentication is None:
        raise NoSuchUserException()

    return authentication
