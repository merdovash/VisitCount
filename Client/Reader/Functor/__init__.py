from abc import abstractmethod

from PyQt5.QtWidgets import QTableWidget

from Client.IProgram import IProgram
from DataBase2 import Professor, Session


class ReaderIsNotPrepared(Exception):
    def __init__(self):
        super().__init__('OnRead is not prepared. Please call OnRead.prepare first')


class OnRead:
    professor: Professor
    table: QTableWidget
    session: Session

    on_error: callable
    on_warning: callable
    on_finish: callable
    on_silent_message: callable

    _prepared = False

    @staticmethod
    def prepare(program: IProgram, table, session: Session):
        OnRead.professor = program.professor
        OnRead.table = table
        OnRead.session = session

        OnRead.on_error = program.window.error.emit
        OnRead.on_warning = program.window.ok_message.emit
        OnRead.on_silent_message = program.window.message.emit

        OnRead._prepared = True

    def method(self, type_, *args, **kwargs):
        if OnRead._prepared:
            return type_(*args, **kwargs)
        else:
            raise ReaderIsNotPrepared()

    @abstractmethod
    def __call__(self, card_id):
        raise NotImplementedError()
