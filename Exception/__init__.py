class BisitorException(Exception):
    CODE = None
    msg = None


class NoSuchUserException(BisitorException):
    CODE = 1
    msg = "no such user"


class InvalidPOSTDataException(BisitorException):
    def __init__(self, msg):
        self.msg = f'{InvalidPOSTDataException.msg}: {msg}'

    CODE = 2
    msg = 'you send wrong data'


def recreateException(CODE, msg) -> BisitorException:
    d = {1: NoSuchUserException,
         2: InvalidPOSTDataException}

    return d[int(CODE)](msg)
