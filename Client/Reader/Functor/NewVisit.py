from typing import List

from PyQt5.QtCore import QObject, pyqtSignal
from sqlalchemy import inspect

from Client.Reader.SerialReader import RFIDReader
from DataBase2 import Lesson, Student, Visitation
from Domain.Exception import StudentNotFoundException, TooManyStudentsFoundException


class MarkVisit(QObject):
    new_visit = pyqtSignal('PyQt_PyObject', 'PyQt_PyObject', 'PyQt_PyObject')

    def __init__(self, students: List[Student], lesson: Lesson, **kwargs):
        super().__init__()
        self.reader = RFIDReader.instance("начать регистрацию студентов", **kwargs)
        self.reader.card_id.connect(self._new_visit)

        self.students = students
        self.lesson = lesson

    def _new_visit(self, card_id):
        students = list(filter(lambda x: int(x.card_id) == int(card_id), self.students))
        if len(students) == 0:
            raise StudentNotFoundException()
        elif len(students) == 1:
            student = students[0]
            visit = Visitation.get_or_create(inspect(student).session, student_id=student.id, lesson_id=self.lesson.id)
            self.new_visit.emit(visit, student, self.lesson)
        else:
            raise TooManyStudentsFoundException(students)

    def stop(self):
        self.reader.card_id.disconnect(self._new_visit)
