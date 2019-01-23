from PyQt5.QtCore import pyqtSlot
from PyQt5.QtWidgets import QMessageBox
from sqlalchemy import inspect

from Client.Reader.SerialReader import RFIDReader
from DataBase2 import Student
from Domain.functools.Format import format_name


class RegisterCard(QMessageBox):
    def __init__(self, student: Student, parent, *__args):
        super().__init__(parent)

        self.reader = RFIDReader.instance()
        if self.reader is None:
            raise Exception()
        self.reader.card_id.connect(self.set_new_card_id)
        self.student = student

        self.setWindowTitle("Регистрация карты")
        self.setText(f"Для регистрации приложите карту {format_name(student, {'gent'})} к считывателю.\n"
                     "После регистрации окно автоматически закроется.")
        self.addButton(QMessageBox.Cancel)
        self.exec_()

    @pyqtSlot('PyQt_PyObject', name='set_new_card_id')
    def set_new_card_id(self, card_id):
        print('gggggg')
        self.setText("Успешно записано")
        self.student.card_id = card_id
        inspect(self.student).session.commit()
        self.close()
        self.reader.card_id.disconnect(self.set_new_card_id)




