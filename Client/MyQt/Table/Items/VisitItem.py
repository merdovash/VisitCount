from PyQt5.QtCore import QPoint, Qt
from PyQt5.QtGui import QColor
from PyQt5.QtWidgets import QMenu, QTableWidget

from Client.Domain.Data import find
from Client.IProgram import IProgram
from Client.MyQt.Table.Items import MyTableItem, AbstractContextItem
from Client.test import safe
from DataBase.Types import format_name
from DataBase2 import Visitation, Student, Lesson


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
        self.student = student
        self.lesson = lesson
        self.visitation = find(lambda x: x.student == self.student, lesson.visitations)

        super().__init__()
        self.program: IProgram = program
        self.table: QTableWidget = table
        self.setTextAlignment(Qt.AlignCenter)
        self.visit_data = [0, 0]
        self.update()

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
        assert visitation.student == self.student and visitation.lesson == self.lesson, "wrong visitation given"
        self.visitation = visitation
        self.table.viewport().update()

    def update(self):
        """
        updates view of item
        """
        if self.status == VisitItem.Status.Visited:
            self.setText("+")
            self.setBackground(MyTableItem.CurrentLessonColor if self.current else VisitItem.Color.Visited)
            self.visit_data = [1, 1]
        elif self.status == VisitItem.Status.NotVisited:
            self.setText("-")
            self.setBackground(MyTableItem.CurrentLessonColor if self.current else VisitItem.Color.NotVisited)
            self.visit_data = [0, 1]
        elif self.status == VisitItem.Status.NoInfo:
            self.setText("")
            self.setBackground(MyTableItem.CurrentLessonColor if self.current else VisitItem.Color.NoInfo)
            self.visit_data = [0, 0]

    def show_context_menu(self, pos):
        # TODO: insert new visits in DB
        """
        overrides base _method
        show context menu on this item
        :param pos: mouse position
        """
        plus = QPoint()
        plus.setX(0)
        plus.setY(25)

        menu = QMenu()
        menu.move(pos + plus)

        menu.addAction("Информация", self._show_info)
        if not self.program['marking_visits']:
            if self.status == VisitItem.Status.NotVisited:
                menu.addAction("Отметить посещение", self._set_visited_by_professor)
                if self.student == VisitItem.Status.Visited:
                    menu.addAction("Отменить запись", self._del_visit_by_professor)
        menu.exec_()

    @safe
    def _show_info(self):
        msg = "{} {}посетил занятие {}".format(format_name(self.student),
                                               "" if self.status == VisitItem.Status.Visited else "не ",
                                               self.lesson.date)
        self.program.window.message.emit(msg, False)
        # RFIDReader.instance()._method = nothing

    @safe
    def _set_visited_by_professor(self):
        if self.program.reader() is not None:
            self.program.window.message.emit("Приложите карточку преподавателя для подтверждения", False)
            self.program.reader().on_read_once(self._set_visited_by_professor_onReadCard)
        else:
            self.program.window.error.emit("Подключите считыватель для подвтерждения внесения изменений.")

    def _set_visited_by_professor_onReadCard(self, card_id):
        professor_card_id = self.program.professor.card_id
        if professor_card_id is not None and professor_card_id != 'None':
            if int(card_id) == int(professor_card_id):
                self.program.window.message.emit("Подтвеждено")
                visitation = Visitation.new(self.student, self.lesson)
                self.set_visitation(visitation)
            else:
                self.program.window.error.emit("Считанная карта не совпадает с картой преподавателя")
                # RFIDReader.instance()._method = nothing
        else:
            self.program.window.error.emit('У вас не зарегистрирована карта.<br>'
                                           'Пожалуйста зрегистрируйте карту в меню "Файл"->"Зарегистрирвоать карту"')

    def _del_visit_by_professor(self):
        self.visitation.delete()


class VisitItemFactory:
    def __init__(self, program: IProgram, table: QTableWidget):
        self.program = program
        self.table = table

    def create(self, student, lesson) -> VisitItem:
        return VisitItem(self.table, self.program, student, lesson)
