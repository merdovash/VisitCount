from PyQt5.QtCore import pyqtSlot, pyqtSignal
from PyQt5.QtWidgets import QMessageBox
from sqlalchemy import inspect

from Client.Reader.SerialReader import RFIDReader
from DataBase2 import IPerson
from Domain.MessageFormat import inflect, Case


class RegisterCardProcess(QMessageBox):
    success = pyqtSignal()

    def __init__(self, user: IPerson, parent, *__args):
        super().__init__(parent)

        self.reader = RFIDReader.instance(f"зарегистрировать карту {inflect(user.__type_name__, Case.РОДИТЕЛЬНЫЙ)}")
        if self.reader is None:
            raise Exception()
        self.reader.card_id.connect(self.set_new_card_id)
        self.user = user

        self.setWindowTitle("Регистрация карты")
        self.setText(f"Для регистрации приложите карту {user.full_name(Case.РОДИТЕЛЬНЫЙ)} к считывателю.\n"
                     "После регистрации окно автоматически закроется.")
        self.addButton(QMessageBox.Cancel)
        self.exec_()

    @pyqtSlot('PyQt_PyObject', name='set_new_card_id')
    def set_new_card_id(self, card_id):
        self.setText("Успешно записано")
        self.user.card_id = card_id
        inspect(self.user).session.commit()
        self.reader.card_id.disconnect(self.set_new_card_id)
        self.close()
