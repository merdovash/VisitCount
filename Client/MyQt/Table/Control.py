from Client.MyQt.Window import AbstractWindow
from Client.Reader.Functor import OnRead
from Client.Reader.Functor.NewVisit import NewVisitOnRead
from DataBase2 import Lesson, Discipline
from DataBase2.Types import format_name
from Domain import Action
from Domain.Exception import UnnecessaryActionException
from Domain.functools.List import find


class IControl:
    pass


class VisitTableControl(IControl):
    __slots__ = ('window', 'table', 'selector', 'reader', 'professor', 'session', 'current_lesson',
                 'current_discipline', 'current_groups')

    _instance = None

    @staticmethod
    def instance():
        if VisitTableControl._instance is None:
            raise Exception(f'{VisitTableControl} is not created')
        else:
            return VisitTableControl._instance

    def __init__(self, window, table, selector, reader: callable, professor, session):
        assert isinstance(window, AbstractWindow), window

        self.selector = selector
        self.window: AbstractWindow = window
        self.professor = professor
        self.current_lesson = None
        self.current_discipline = None
        self.current_groups = None
        self._is_lesson_started = False
        self.table = table
        self.reader: function = reader
        self.session = session

        OnRead.prepare(window.program, table, session)

    def change_discipline(self, discipline):
        assert isinstance(discipline, Discipline)
        self.current_discipline = discipline

        self.table.set_discipline(discipline)

    def change_group(self, groups):
        assert isinstance(groups, (list, set))
        self.current_groups = groups

        self.table.set_group(groups)

    def select_lesson(self, lesson):
        assert isinstance(lesson, Lesson), lesson
        # assert lesson in self.table.lessons
        if self.isLessonStarted():
            self.window.ok_message.emit('Невозможно выбрать другое занятие, так как идет учет. Снчала завершите учет.')
            return
        else:
            self.current_lesson = lesson

            self.table.set_lesson(lesson)

            if self.selector.lesson.current() != lesson:
                self.selector.lesson.blockSignals(True)
                self.selector.lesson.setCurrent(lesson)
                self.selector.lesson.blockSignals(False)

    def start_lesson(self):
        print('Control start lesson')
        if self.reader() is not None:
            self._is_lesson_started = True
            self.reader().on_read(NewVisitOnRead(self.current_groups, self.current_lesson))
            self.selector.setEnabledControl(False)
            self.selector.switchBtnAction(False)
            try:
                Action.start_lesson(self.current_lesson, self.professor)
                self.table.force_repaint()
            except UnnecessaryActionException:
                pass
        else:
            self.window.ok_message.emit('Считыватель не обнаружен. Ведение учёта невозможно.')

    def end_lesson(self):
        self._is_lesson_started = False
        self.selector.setEnabledControl(True)
        self.selector.switchBtnAction(True)
        self.reader().stop_read()

    def _new_visit(self, card_id):
        print('Control new visit', end='')
        student = find(lambda x: x.card_id == card_id, self.table.students_header.keys())
        if student is not None:
            # записываем в БД
            visit = Action.new_visitation(student, self.current_lesson, self.professor.id, self.session)
            print(visit)

            # отмечаем в таблице
            row_index = self.table.students_header[student].index
            col_index = self.table.lessons_header[self.current_lesson].index
            self.table.visits[row_index, col_index].set_visitation(visit)
            self.table.force_repaint()

            # выводим сообщение
            self.window.message.emit(f'{format_name(student)} отмечен', False)
        else:
            print('failed')

    def isLessonStarted(self) -> bool:
        return self._is_lesson_started

    def currentLesson(self) -> Lesson:
        return self.current_lesson
