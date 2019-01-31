from Domain.Exception import BisitorException


class AuthenticationException(BisitorException):
    _title = "Ошибка аутентификации"
    _mask = "{}"

    def __init__(self, action='входа в систему'):
        self._msg = action


class InvalidLoginException(AuthenticationException):
    _mask = "Во время {} вы неверно указали логин."


class InvalidPasswordException(AuthenticationException):
    _mask = "Во время {} вы неверно указали пароль."


class InvalidUidException(AuthenticationException):
    pass


class UnothorizedError(AuthenticationException):
    _title = "ошибка доступа"
    _mask = "При {} произошла попытка получения доступа к правам недоступного пользователя"
