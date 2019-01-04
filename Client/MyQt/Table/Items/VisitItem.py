from PyQt5.QtCore import Qt, QRect, QPoint
from PyQt5.QtGui import QColor, QPen, QPixmap, QPainter
from PyQt5.QtWidgets import QMenu, QTableWidget
from sqlalchemy.orm.exc import ObjectDeletedError

from Client.IProgram import IProgram
from Client.MyQt.ColorScheme import Color
from Client.MyQt.Table.Items import MyTableItem, AbstractContextItem, IDraw
from Client.MyQt.utils import Signaler
from DataBase2 import Visitation, Student, Lesson, session_user
from Domain import Action
from Domain.functools.Format import format_name
from Domain.functools.List import find


class VisitItem(IDraw, MyTableItem, AbstractContextItem):
    """
    item represents visitation
    """
    select_border_pen = QPen(Color.secondary_light)
    select_border_pen.setWidthF(1.3)
    image = {}

    @session_user
    def draw(self, painter, rect: QRect, highlighted=False, selected=False):
        code = (highlighted, selected, self.isVisit(), self.lesson.completed, rect.width(), rect.height())
        if code not in VisitItem.image.keys():
            pix = QPixmap(rect.size())

            p = QPainter(pix)

            r = QRect(QPoint(0, 0), rect.size())

            p.fillRect(r, self.get_color(highlighted=highlighted, selected=selected))

            p.setPen(self.textPen)
            p.drawText(r, Qt.AlignCenter, self.text())

            p.setPen(self.border_pen if not selected else self.select_border_pen)
            p.drawRect(r)

            VisitItem.image[code] = pix.toImage()

            p.end()
        painter.drawImage(rect, VisitItem.image[code])

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

        self.info_changed = Signaler()

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

    def isVisit(self):
        return self.visitation is not None

    def set_visitation(self, visitation: Visitation):
        # assert visitation.student == self.student and visitation.lesson == self.lesson, "wrong visitation given"
        self.visitation = visitation
        self.update()
        self.info_changed()

    def remove_visitation(self):
        self.visitation = None
        self.update()
        self.info_changed()

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

    def get_color(self, highlighted=False, selected=False):
        if self.status == VisitItem.Status.Visited:
            color = MyTableItem.CurrentLessonColor if self.current else VisitItem.Color.Visited

        elif self.status == VisitItem.Status.NotVisited:
            color = MyTableItem.CurrentLessonColor if self.current else VisitItem.Color.NotVisited

        elif self.status == VisitItem.Status.NoInfo:
            color = MyTableItem.CurrentLessonColor if self.current else VisitItem.Color.NoInfo

        if highlighted:
            color = Color.to_accent(color)

        if selected:
            color = Color.to_select(color)

        return color

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
            visitation = Visitation(student_id=self.student.id, lesson_id=self.lesson.id)
            self.program.professor.session.add(visitation)
            self.program.professor.session.commit()

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
            self.visitation.delete()
            self.program.professor.session.commit()
            self.remove_visitation()
        except ObjectDeletedError:
            self.visitation = find(lambda x: x.student_id == self.student.id, Visitation.of(self.lesson))
            self._del_visit_by_professor()


class VisitItemFactory:
    def __init__(self, program: IProgram, table: QTableWidget):
        self.program = program
        self.table = table

    def create(self, student, lesson) -> VisitItem:
        visit_item = VisitItem(self.table, self.program, student, lesson)
        visit_item.info_changed += self.table.cell_changed

        return visit_item
