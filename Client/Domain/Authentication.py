from DataBase2 import Auth
from Exception import NoSuchUserException


def Authentication(**kwargs) -> Auth:
    authentication = Auth.log_in(**kwargs)

    if authentication is None:
        raise NoSuchUserException()

    return authentication
