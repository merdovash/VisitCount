from typing import List

from PyQt5.QtCore import pyqtSignal
from PyQt5.QtWidgets import QWidget

from DataBase2 import ISession, Professor


class Step:
    def __init__(self, description, tooltip, completed=False):
        self.description = description
        self.tooltip = tooltip
        self.completed = completed


class AbstractLoadingWizard(QWidget):
    steps: List[Step]
    step = pyqtSignal('PyQt_PyObject')
    revoke_step = pyqtSignal('PyQt_PyObject')
    steps_changed = pyqtSignal('PyQt_PyObject')

    loading_session: ISession
    professor: Professor
