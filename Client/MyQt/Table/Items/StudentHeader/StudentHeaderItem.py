from PyQt5.QtGui import QColor
from PyQt5.QtWidgets import QMenu, QTableWidgetItem

from Client.IProgram import IProgram
from Client.MyQt.Table.Items import AbstractContextItem
from Client.test import safe
from DataBase.Types import format_name
from DataBase2 import Student


class StudentHeaderItem(QTableWidgetItem, AbstractContextItem):
    def __init__(self, program: IProgram, student: Student, *__args):
        super().__init__(*__args)
        self.program: IProgram = program

        self.student_name = format_name(student)
        self.setText(self.student_name)
        self.student = student

        if student.card_id is None or student.card_id == 'None':
            self.setBackground(QColor(220, 180, 0))

        self.register_process = False

    @safe
    def show_context_menu(self, pos):
        """
        override base _method

        show context menu:
            1) register card / stop register card
            2) show card_id
        :param pos:
        """
        menu = QMenu()
        print(pos)
        menu.move(pos)
        # if not WorkingData.instance().marking_visits:
        if not self.register_process:
            menu.addAction("Зарегистрировать карту", self._register_student_card)
        else:
            menu.addAction("Отменить регистрацию карты", self.stop_card_register_process)
        menu.addAction("Показать номер карты", lambda: self.program.window.message.emit(
            f'{self.student_name} - "{self.student.card_id}"', False))
        menu.exec_()

    @safe
    def _register_student_card(self):
        if self.program.reader() is not None:
            self.program.reader().on_read_once(self._register_student_card_onRead)

            self.program.window.message.emit("Приложите карту {} для регистрации".format(self.student_name), True)

            self.register_process = True

        else:
            self.program.window.error.emit("Для регистрации карты необходимо подключение к считывателю")

    @safe
    def _register_student_card_onRead(self, card_id):
        self.stop_card_register_process()
        print(card_id)

        self.student.card_id = card_id

        if self.student["card_id"] is not None:
            self.program.window.message.emit("Студенту {} перезаписали номер карты".format(self.student_name), True)
        else:
            self.program.window.message.emit("Студенту {} записали номер карты".format(self.student_name), True)
            self.setBackground(QColor(255, 255, 255))

    def stop_card_register_process(self):
        self.program.window.message.emit("Регистрация карты остановлена", False)
        self.register_process = False
        self.program.reader().remove_temporary_function()
