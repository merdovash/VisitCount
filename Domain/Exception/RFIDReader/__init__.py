from Domain.Exception import BisitorException


class RFIDReaderException(BisitorException):
    _title = "Ошибка считывателя"
    _mask = "При попытке {} произошло непредвиденное поведение считывателя. Операция прервана."


class RFIDReaderNotFoundException(RFIDReaderException):
    _title = "Считыватель не найден"
    _mask = "При попытке {} считыватель не был онаружен. Операция прервана."


class RFIDReaderHasGoneAwayException(RFIDReaderException):
    _title = "Считыватель перестал отвечать"
    _mask = "Во время процедуры '{}' считыватель перестал отвечать." \
            "\nВозможно он был отключен. Убедитесь, что он подключен."

