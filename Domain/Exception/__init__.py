from typing import Callable

try:
    from PyQt5.QtWidgets import QMessageBox
except ModuleNotFoundError:
    pass


class BisitorException(Exception):
    _title = "Ошибка программы"
    _mask = "Произошла неизвестная ошибка {}"

    _msg: str = None

    def show(self, parent=None):
        QMessageBox().critical(parent, self.title(), self.message())
        self._callback()

    def title(self) -> str:
        return self._title

    def message(self) -> str:
        return self._mask.format(self._msg)

    def _callback(self):
        pass

    def __init__(self, msg: str = "неуказанное действие", window=None, callback: Callable[[], None] = lambda: None, **kwargs):
        self.window = window
        self._msg = msg
        self._callback = callback


class StudentNotFoundException(BisitorException):
    _title = "Студента нет в списке"
    _mask = """
    Во время {} студент не обнаружен.\n
    Убедитесь, что студент зарегистрировал карту.\n
    Если студент не зарегистрировал карту:\n
    \t1) Остановите учет,
    \t2) Зарегистрируйте карту,
    \t3) Возобновите учет.
    """


class TooManyStudentsFoundException(BisitorException):
    _title = "Слишком много студентов обнаружено"
    _mask = "Во время {} обнаружено слишком много студентов с одинковыми идентификаторами карт."

    def __init__(self, students, msg=None):
        super().__init__(msg)
        self.students = students


class BisitorNotImplementedError(BisitorException):
    _title = "Ещё не реализованное действие"
    _mask = "Не переживайте, ничего не сломалось. \n" \
            "Вы попытались совершить действие которое еще не реализовано. "
