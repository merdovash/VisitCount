from PyQt5.QtCore import Qt
from PyQt5.QtGui import QColor
from PyQt5.QtWidgets import QMenu, QTableWidget
from sqlalchemy.orm.exc import ObjectDeletedError

from Client.IProgram import IProgram
from Client.MyQt.Table.Items import MyTableItem, AbstractContextItem
from DataBase2 import Visitation, Student, Lesson
from DataBase2.Types import format_name
from Domain import Action
from Domain.functools.List import find


class VisitItem(MyTableItem, AbstractContextItem):
    """
    item represents visitation
    """

    class Status(int):
        Visited = 1
        NoInfo = 2
        NotVisited = 0

    class Color(QColor):
        Visited = QColor("#ffff00")
        NotVisited = QColor("#ffffff")
        NoInfo = QColor("#ffffff")

    def __init__(self, table: QTableWidget, program: IProgram,
                 student: Student, lesson: Lesson):
        self.ready = False
        self.student = student
        self.lesson = lesson
        self.visitation = find(lambda x: x.student == self.student, lesson.visitations)

        super().__init__()
        self.program: IProgram = program
        self.table: QTableWidget = table
        self.setTextAlignment(Qt.AlignCenter)
        self.visit_data = [0, 0]
        self.update()

        self.safe = False
        self.ready = True

    @property
    def status(self):
        if self.lesson.completed:
            if self.visitation is not None:
                return VisitItem.Status.Visited
            else:
                return VisitItem.Status.NotVisited
        else:
            return VisitItem.Status.NoInfo

    def set_visitation(self, visitation: Visitation):
        # assert visitation.student == self.student and visitation.lesson == self.lesson, "wrong visitation given"
        self.visitation = visitation
        self.update()

    def text(self):
        self.update()
        return super().text()

    def update(self):
        """
        updates view of item
        """
        status = self.status
        if status == VisitItem.Status.Visited:
            self.visit_data = [1, 1]
            self.setText("+")
            self.setBackground(MyTableItem.CurrentLessonColor if self.current else VisitItem.Color.Visited)

        elif status == VisitItem.Status.NotVisited:
            self.visit_data = [0, 1]
            self.setText("-")
            self.setBackground(MyTableItem.CurrentLessonColor if self.current else VisitItem.Color.NotVisited)

        elif status == VisitItem.Status.NoInfo:
            self.visit_data = [0, 0]
            self.setText("")
            self.setBackground(MyTableItem.CurrentLessonColor if self.current else VisitItem.Color.NoInfo)

    def get_color(self):
        if self.status == VisitItem.Status.Visited:
            return MyTableItem.CurrentLessonColor if self.current else VisitItem.Color.Visited

        elif self.status == VisitItem.Status.NotVisited:
            return MyTableItem.CurrentLessonColor if self.current else VisitItem.Color.NotVisited

        elif self.status == VisitItem.Status.NoInfo:
            return MyTableItem.CurrentLessonColor if self.current else VisitItem.Color.NoInfo

    def show_context_menu(self, pos):
        # TODO: insert new visits in DB
        """
        overrides base _method
        show context menu on this item
        :param pos: mouse position
        """
        # plus = self.table.pos()

        menu = QMenu()
        menu.move(pos)

        menu.addAction("Информация", self._show_info)
        if not self.program['marking_visits']:
            if self.status == VisitItem.Status.NotVisited:
                menu.addAction("Отметить посещение", self._set_visited_by_professor)
            elif self.status == VisitItem.Status.Visited:
                menu.addAction("Отменить запись", self._del_visit_by_professor)
        menu.exec_()

    def _show_info(self):
        msg = "{} {}посетил занятие {}".format(format_name(self.student),
                                               "" if self.status == VisitItem.Status.Visited else "не ",
                                               self.lesson.date)
        self.program.window.message.emit(msg, False)
        # RFIDReader.instance()._method = nothing

    def _set_visited_by_professor(self):
        if self.safe:
            if self.program.reader() is not None:
                self.program.window.message.emit("Приложите карточку преподавателя для подтверждения", False)
                self.program.reader().on_read_once(self._set_visited_by_professor_onReadCard)
            else:
                self.program.window.error.emit("Подключите считыватель для подвтерждения внесения изменений.")
        else:
            self._set_visited_by_professor_onReadCard(None)

    def _set_visited_by_professor_onReadCard(self, card_id):
        def create():
            visitation = Action.new_visitation(self.student, self.lesson, self.program.professor.id)
            self.set_visitation(visitation)
            self.program.window.message.emit("Подтвеждено", False)

        if self.safe:
            professor_card_id = self.program.professor.card_id
            if professor_card_id is not None and professor_card_id != 'None':
                if int(card_id) == int(professor_card_id):
                    create()
                else:
                    self.program.window.error.emit("Считанная карта не совпадает с картой преподавателя")
                    # RFIDReader.instance()._method = nothing
            else:
                self.program.window.error.emit('У вас не зарегистрирована карта.<br>'
                                               'Пожалуйста зрегистрируйте карту в меню "Файл"->"Зарегистрирвоать карту"')
        else:
            create()

    def _del_visit_by_professor(self):
        assert isinstance(self.visitation, Visitation), f"self.visitation is {type(self.visit_data)}"
        try:
            Action.remove_visitation(self.visitation, self.program.professor.id)
            self.visitation = None
            self.update()
        except ObjectDeletedError:
            self.visitation = find(lambda x: x.student_id == self.student.id, Visitation.of(self.lesson))
            self._del_visit_by_professor()


class VisitItemFactory:
    def __init__(self, program: IProgram, table: QTableWidget):
        self.program = program
        self.table = table

    def create(self, student, lesson) -> VisitItem:
        return VisitItem(self.table, self.program, student, lesson)
