from typing import Dict

from PyQt5.QtCore import QObject, pyqtSignal

from Domain.Structures.DictWrapper import Structure


class _ClientWorkerMetaClass(type):
    def __new__(cls, name, bases, body):
        if 'on_response' not in body:
            raise TypeError('you have to implement ')
        super().__new__(cls, name, bases, body)


class ClientWorker(QObject):
    finish = pyqtSignal('PyQt_PyObject')

    address = str
    data: Dict or Structure

    def __init__(self):
        super().__init__()

    def on_response(self, received_data: Dict, progress_bar):
        raise NotImplementedError()
