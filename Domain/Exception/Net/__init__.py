from Domain.Exception import BisitorException


class NetException(BisitorException):
    pass


class InvalidPOSTDataException(NetException):
    def __init__(self, msg):
        self.msg = f'{InvalidPOSTDataException.msg}: {msg}'

    msg = 'you send wrong data'
