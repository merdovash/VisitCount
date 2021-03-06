from typing import Dict

from PyQt5.QtCore import QObject, pyqtSignal

from Domain.Structures.DictWrapper import Structure


class ClientWorker(QObject):
    """
    Базовый класс для всех
    """
    finish = pyqtSignal('PyQt_PyObject')

    address = str
    data: Dict or Structure

    def __init__(self):
        super().__init__()

    def on_response(self, received_data: Dict, progress_bar):
        raise NotImplementedError()
