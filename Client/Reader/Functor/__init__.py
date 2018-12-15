from abc import abstractmethod

from PyQt5.QtCore import QObject
from PyQt5.QtCore import pyqtSignal
from PyQt5.QtWidgets import QTableWidget

from Client.IProgram import IProgram
from Client.MyQt.Window.interfaces import IDataBaseUser
from DataBase2 import Professor, Session


class ReaderIsNotPrepared(Exception):
    def __init__(self):
        super().__init__('OnRead is not prepared. Please call OnRead.prepare first')


class OnRead(QObject, IDataBaseUser):
    professor: Professor
    widget: QTableWidget
    session: Session

    error = pyqtSignal(str)
    message = pyqtSignal(str, bool)
    warning = pyqtSignal(str)

    _prepared = False

    @staticmethod
    def prepare(program: IProgram, widget, session: Session, window=None):
        OnRead.professor = program.professor if hasattr(program, 'professor') else None
        OnRead.widget = widget
        OnRead.session = session

        window = window if window is not None else program.window

        OnRead.on_error = window.on_error
        OnRead.on_warning = window.on_ok_message
        OnRead.on_message = window.on_show_message

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
        if not OnRead._prepared:
            raise ReaderIsNotPrepared()
        QObject.__init__(self)
        IDataBaseUser.__init__(self, OnRead.session)

        self.error.connect(OnRead.on_error)
        self.warning.connect(OnRead.on_warning)
        self.message.connect(OnRead.on_message)
