from Client.Reader.Functor import OnRead
from DataBase2 import Student
from DataBase2.Types import format_name
from Domain import Action
from Domain.functools.List import find


class NewVisitOnRead(OnRead):
    def __call__(self, card_id):
        print('Control new visit', end='')
        student = find(lambda x: x.card_id == card_id, self.widget.students_header.keys())
        if student is not None:
            # записываем в БД
            visit = Action.new_visitation(
                student=student,
                lesson=self.lesson,
                professor_id=self.professor.id,
                session=self.session)

            # отмечаем в таблице
            row_index = self.widget.students_header[student].index
            col_index = self.widget.lessons_header[self.lesson].index
            self.widget.visits[row_index, col_index].set_visitation(visit)
            self.widget.force_repaint()

            # выводим сообщение
            self.message.emit(f'{format_name(student)} отмечен', False)
        else:
            self.message.emit('Студент не обнаружен', False)

    def __init__(self, groups, lesson):
        OnRead.__init__(self)

        self.students = Student.of(groups)
        self.lesson = lesson
