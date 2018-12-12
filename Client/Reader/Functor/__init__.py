from abc import abstractmethod

from PyQt5.QtCore import QObject
from PyQt5.QtCore import pyqtSignal
from PyQt5.QtWidgets import QTableWidget

from Client.IProgram import IProgram
from DataBase2 import Professor, Session


class ReaderIsNotPrepared(Exception):
    def __init__(self):
        super().__init__('OnRead is not prepared. Please call OnRead.prepare first')


class OnRead(QObject):
    professor: Professor
    table: QTableWidget
    session: Session

    error = pyqtSignal(str)
    message = pyqtSignal(str, bool)
    warning = pyqtSignal(str)

    _prepared = False

    @staticmethod
    def prepare(program: IProgram, table, session: Session):
        OnRead.professor = program.professor
        OnRead.table = table
        OnRead.session = session

        OnRead.on_error = program.window.on_error
        OnRead.on_warning = program.window.on_ok_message
        OnRead.on_message = program.window.on_show_message

        OnRead._prepared = True

    def method(self, type_, *args, **kwargs):
        if OnRead._prepared:
            return type_(*args, **kwargs)
        else:
            raise ReaderIsNotPrepared()

    @abstractmethod
    def __call__(self, card_id):
        raise NotImplementedError()

    def __init__(self):
        super().__init__()

        self.error.connect(OnRead.on_error)
        self.warning.connect(OnRead.on_warning)
        self.message.connect(OnRead.on_message)
