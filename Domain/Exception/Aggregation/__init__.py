from Domain.Exception import BisitorException


class NoDataError(BisitorException):
    _title = "Нет данных"
    _mask = "По выбранным показателям нет данных {}"

    _msg: str = None
