from Domain.Exception import BisitorException


class AuthenticationException(BisitorException):
    pass


class InvalidLoginException(AuthenticationException):
    def __init__(self, msg='no such login'):
        super().__init__(f"Invalid login: {msg}")


class InvalidPasswordException(AuthenticationException):
    def __init__(self, msg=None):
        super().__init__(f'Invalid password {msg}')


class InvalidUidException(AuthenticationException):
    def __init__(self, msg=None):
        super().__init__(f'Invalid uid token {msg}')


class UnothorizedError(AuthenticationException):
    _title = "ошибка доступа"
    _mask = "При {} произошла попытка получения доступа к правам недоступного пользователя"
