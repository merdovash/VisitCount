from Client.Reader.Functor import OnRead
from DataBase2 import Student
from Domain import Action
from Domain.functools.List import find


class NewVisitOnRead(OnRead):
    def __call__(self, card_id):
        student = find(lambda student: student.card_id == card_id, self.students)

        if student is not None:
            Action.new_visitation(student, self.lesson, self.professor.id, self.session)

            self.table.new_visit(student=student, lesson=self.lesson)

    def __init__(self, table, groups, lesson, professor, session):
        self.students = Student.of(groups)
        self.lesson = lesson
        self.professor = professor
        self.session = session
        self.table = table
