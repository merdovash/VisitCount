from PyQt5.QtCore import QPoint, Qt
from PyQt5.QtGui import QColor
from PyQt5.QtWidgets import QMenu, QTableWidget

from Client.MyQt.Table.Items import MyTableItem, AbstractContextItem
from Client.test import safe


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

    def __init__(self, table: QTableWidget, program,
                 status: Status = Status.NoInfo, student: dict = None,
                 lesson: dict = None):
        super().__init__()
        self.db = program.db
        self.program = program
        self.table: QTableWidget = table
        self.setTextAlignment(Qt.AlignCenter)
        self.status = status
        self.visit_data = [0, 0]
        self.update()

        self.student = student
        self.lesson = lesson

    def set_visit_status(self, status: 'VisitItem.Status' or int):
        """
        sets status of item to :param status:
        :param status:
        :return:
        """
        if self.status == status:
            return
        elif (self.status == VisitItem.Status.NotVisited and status == VisitItem.Status.Visited) \
                or (self.status == VisitItem.Status.NoInfo and status == VisitItem.Status.NotVisited):
            self.status = status
            self.update()
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
                # if self.student == VisitItem.Status.Visited:
                #     menu.addAction("Отменить запись", self._del_visit_by_professor)
        menu.exec_()

    @safe
    def _show_info(self):
        msg = "{} {}.{}. {}посетил занятие {}".format(self.student["last_name"],
                                                      self.student["first_name"][0],
                                                      self.student["middle_name"][0],
                                                      "" if self.status == VisitItem.Status.Visited else "не ",
                                                      self.lesson["date"])
        self.program.window.message.emit(msg)
        # RFIDReader.instance()._method = nothing

    @safe
    def _set_visited_by_professor(self):
        if self.program.reader() is not None:
            self.program.window.message.emit("Приложите карточку преподавателя для подтверждения")
            self.program.reader().on_read_once(self._set_visited_by_professor_onReadCard)
        else:
            self.program.window.emit("Подключите считыватель для подвтерждения внесения изменений.")

    def _set_visited_by_professor_onReadCard(self, card_id):
        if int(card_id) == int(self.program['professor']["card_id"]):
            self.program.window.message.emit("Подтвеждено")
            self.db.add_visit(
                student_id=self.student["id"],
                lesson_id=self.lesson["id"]
            )
            self.set_visit_status(VisitItem.Status.Visited)
        else:
            self.program.window.message.emit("Ошибка")
            # RFIDReader.instance()._method = nothing
