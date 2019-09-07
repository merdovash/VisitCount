from typing import List

from PyQt5.QtCore import QObject, pyqtSignal, Qt
from PyQt5.QtWidgets import QWidget, QPushButton, QLabel, QVBoxLayout, QHBoxLayout, QCheckBox
from sqlalchemy import inspect

from Client.MyQt.Widgets.ComboBox import QMComboBox
from Client.Reader.SerialReader import RFIDReader
from DataBase2 import Lesson, Student, Visitation, Group
from Domain.Exception import StudentNotFoundException, TooManyStudentsFoundException, BisitorException

from Parser import Args


class StudentSelector(QWidget):
    select = pyqtSignal('PyQt_PyObject')
    cancel = pyqtSignal()

    def __init__(self, students: List[Student], parent=None):
        super().__init__(parent)

        self.setWindowModality(Qt.ApplicationModal)

        def fill_combo(with_card):
            self.combo.clear()
            self.combo.addItems(list(filter(lambda student: with_card or student.card_id is None, students)))

        self.label = QLabel("Для введенной карты не обнаружен студент.\n"
                            "Выберите студента для введеной карты из списка ниже.")

        self.combo = QMComboBox(Student)
        self.combo.formatter = lambda student: f'{Group.names(student.groups)} | {student.full_name()}'

        self.show_all_students = QCheckBox("Показать всех студентов")
        self.show_all_students.toggled.connect(fill_combo)

        self.ok_button = QPushButton("Подтвердить")
        self.ok_button.clicked.connect(lambda: self.select.emit(self.combo.current()))

        self.cancel_button = QPushButton("Отмена")
        self.cancel_button.clicked.connect(self.cancel)

        main_layout = QVBoxLayout()
        main_layout.addWidget(self.label)
        main_layout.addWidget(self.show_all_students)
        main_layout.addWidget(self.combo)

        button_layout = QHBoxLayout()
        button_layout.addWidget(self.ok_button)
        button_layout.addWidget(self.cancel_button)

        main_layout.addLayout(button_layout)

        self.setLayout(main_layout)

        fill_combo(self.show_all_students.isChecked())

        self.select.connect(self.close)
        self.cancel.connect(self.close)


class MarkVisitProcess(QObject):
    new_visit = pyqtSignal('PyQt_PyObject', 'PyQt_PyObject', 'PyQt_PyObject')

    def __init__(self, students: List[Student], lesson: Lesson, **kwargs):
        super().__init__()
        try:
            self.reader = RFIDReader.instance("начать регистрацию студентов", **kwargs)
            self.reader.card_id.connect(self._new_visit)
        except BisitorException as be:
            if Args().test:
                pass
            else:
                raise be

        self.students = sorted(
                students,
                key=lambda student: f'{Group.names(student.groups)} | {student.full_name()}')
        self.lesson = lesson

        self.session = inspect(lesson).session

    def _new_visit(self, card_id):
        def mark_visit(student):
            visit = Visitation.get_or_create(self.session, student_id=student.id, lesson_id=self.lesson.id)
            self.session.commit()
            self.session.expire(student)
            self.session.expire(self.lesson)
            self.new_visit.emit(visit, student, self.lesson)

        students = list(filter(lambda x: x.card_id == int(card_id), self.students))
        if len(students) == 0:
            def apply_student(student):
                student.card_id = card_id
                self.session.commit()
                mark_visit(student)

            def reject_card():
                raise StudentNotFoundException()

            student_selector = StudentSelector(self.students)

            student_selector.select.connect(apply_student)
            student_selector.cancel.connect(reject_card)

            student_selector.show()

        elif len(students) == 1:
            mark_visit(students[0])
        else:
            raise TooManyStudentsFoundException(students)

    def stop(self):
        try:
            self.reader.card_id.disconnect(self._new_visit)
        except AttributeError as attr_err:
            if Args().test:
                pass
            else:
                raise attr_err
