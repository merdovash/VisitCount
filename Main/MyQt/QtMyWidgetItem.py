import traceback
from datetime import datetime

from PyQt5.QtCore import Qt, QPoint
from PyQt5.QtGui import QColor, QFont
from PyQt5.QtWidgets import QTableWidgetItem, QMenu, QTableWidget

from DataBase.sql_handler import DataBaseWorker
from Main.MyQt.QtMyCalendar import LessonDateChanger
from Main.MyQt.QtMyStatusBar import QStatusMessage
from Main.MyQt.Time import from_time_to_index
from Main.SerialsReader import RFIDReader, nothing
from Main.Types import WorkingData


class AbstractContextItem:
    def show_context_menu(self, pos):
        pass


class MyTableItem(QTableWidgetItem):
    def __init__(self):
        super().__init__()
        self.color = "#FFFFFF"
        self.current_lesson_color = QColor("#ccccff")
        self.current = False

    def current_lesson(self, b):
        self.current = b
        self.update()

    def update(self):
        pass


class VisitItem(MyTableItem, AbstractContextItem):
    class Status(int):
        Visited = 1
        NoInfo = 2
        NotVisited = 0

    class Data(int):
        Completed = 1
        Visited = 0

    class Color(QColor):
        Visited = QColor("#ffff00")
        NotVisited = QColor("#ffffff")
        NoInfo = QColor("#ffffff")

    def __init__(self, table, status: Status = Status.NoInfo, student: dict = None, lesson: dict = None):
        super().__init__()
        self.table: QTableWidget = table
        self.setTextAlignment(Qt.AlignCenter)
        self.status = status
        self.visit_data = [0, 0]
        self.update()

        self.student = student
        self.lesson = lesson

    def set_visit_status(self, status: 'VisitItem.Status'):
        if self.status == status:
            return
        elif (self.status == VisitItem.Status.NotVisited and status == VisitItem.Status.Visited) \
                or (self.status == VisitItem.Status.NoInfo and status == VisitItem.Status.NotVisited):
            self.status = status
            self.update()
            self.table.viewport().update()

    def update(self):
        if self.status == VisitItem.Status.Visited:
            self.setText("+")
            self.setBackground(self.current_lesson_color if self.current else VisitItem.Color.Visited)
            self.visit_data = [1, 1]
        elif self.status == VisitItem.Status.NotVisited:
            self.setText("-")
            self.setBackground(self.current_lesson_color if self.current else VisitItem.Color.NotVisited)
            self.visit_data = [0, 1]
        elif self.status == VisitItem.Status.NoInfo:
            self.setText("")
            self.setBackground(self.current_lesson_color if self.current else VisitItem.Color.NoInfo)
            self.visit_data = [0, 0]

    def show_context_menu(self, pos):
        # TODO: insert new visits in DB
        plus = QPoint()
        plus.setX(0)
        plus.setY(25)

        menu = QMenu()
        menu.move(pos + plus)

        menu.addAction("Информация", self._show_info)
        if not WorkingData.instance().marking_visits:
            if self.status == VisitItem.Status.NotVisited:
                menu.addAction("Отметить посещение", self._set_visited_by_professor)
                # if self.student == VisitItem.Status.Visited:
                #     menu.addAction("Отменить запись", self._del_visit_by_professor)
        menu.exec_()

    def _show_info(self):
        msg = "{} {}.{}. {}посетил занятие {}".format(self.student["last_name"],
                                                      self.student["first_name"][0],
                                                      self.student["middle_name"][0],
                                                      "" if self.status == VisitItem.Status.Visited else "не ",
                                                      self.lesson["date"])
        QStatusMessage.instance().setText(msg)
        RFIDReader.instance().method = nothing

    def _set_visited_by_professor(self):
        QStatusMessage.instance().setText("Приложите карточку преподавателя для подтверждения")
        RFIDReader.instance().onReadOnce(self._set_visited_by_professor_onReadCard)

    def _set_visited_by_professor_onReadCard(self, card_id):
        if int(card_id) == int(WorkingData.instance().professor["card_id"]):
            QStatusMessage.instance().setText("Подтвеждено")
            DataBaseWorker.instance().add_visit(student_id=self.student["id"], lesson_id=self.lesson["id"])
            self.set_visit_status(VisitItem.Status.Visited)
        else:
            QStatusMessage.instance().setText("Ошибка")
            # RFIDReader.instance().method = nothing


class LessonTypeItem(QTableWidgetItem, AbstractContextItem):
    def __init__(self, lesson_type: int):
        super().__init__()
        self.setTextAlignment(Qt.AlignCenter)
        lesson_type = int(lesson_type)
        if lesson_type == 0:
            self.setText("Л")
            self.setToolTip("Лекция")
        elif lesson_type == 1:
            self.setText("л")
            self.setToolTip("Лабораторная работа")
        else:
            self.setText("П")
            self.setToolTip("Практика")

    def show_context_menu(self, pos):
        # TODO: make start and end function
        if not WorkingData.instance().marking_visits:
            menu = QMenu()
            print(pos)
            menu.move(pos)
            menu.addAction("Начать учет")
            menu.exec_()


class LessonNumberItem(QTableWidgetItem):
    def __init__(self, date: datetime):
        super().__init__()
        self.setTextAlignment(Qt.AlignCenter)
        self.setText(str(from_time_to_index(date)))


class WeekDayItem(QTableWidgetItem):
    rule = ["пн", "вт", "ср", "чт", "пт", "сб", "вс"]

    def __init__(self, date: datetime):
        super().__init__()
        self.setTextAlignment(Qt.AlignCenter)
        self.setText(str(WeekDayItem.rule[date.weekday()]))


class LessonDateItem(QTableWidgetItem, AbstractContextItem):
    def __init__(self, date: datetime, lesson_id: int, parent: 'MainWindow' = None):
        super().__init__()
        self._parent = parent
        self.date = date
        self.lesson_id = lesson_id
        self.setTextAlignment(Qt.AlignCenter)
        self.setText(str(date.day))

    def show_context_menu(self, pos):
        if not WorkingData.instance().marking_visits:
            menu = QMenu()
            menu.move(pos)
            menu.addAction("Перенести занятие", self.move_lesson)
            menu.exec_()

    def move_lesson(self):
        try:
            self.calendar = LessonDateChanger(self.date, self.lesson_id, self._parent)
            self.calendar.show()
        except Exception:
            traceback.print_exc()


month_names = "0,Январь,Февраль,Март,Апрель,Май,Июнь,Июль,Август,Сентябрь,Октябрь,Ноябрь,Декабрь".split(',')


class MonthTableItem(QTableWidgetItem):
    def __init__(self, month_index: int = None, month: str = None):
        super().__init__()
        self.setTextAlignment(Qt.AlignCenter)
        if month is not None:
            self.setText(month)
        elif month_index is not None:
            self.setText(month_names[month_index])
        else:
            self.setText("Месяц")


class PercentItem(QTableWidgetItem):
    absolute = False

    class Font(int):
        Absolute = QFont("SansSerif", 7)
        Percent = QFont("SansSerif", 8)

    class Orientation(int):
        ByLessons = 0
        ByStudents = 1

    def __init__(self, items: list, orientation: 'PercentItem.Orientation', *__args):
        super().__init__(*__args)
        self.items = list(filter(lambda x: type(x) == VisitItem, items))
        self.visit = 0
        self.total = 0
        self.orientation = orientation
        self.refresh()
        if orientation == PercentItem.Orientation.ByLessons:
            self.setTextAlignment(Qt.AlignCenter)
        else:
            self.setTextAlignment(Qt.AlignLeft)

    def calc(self):
        for item in self.items:
            self.total += item.visit_data[VisitItem.Data.Completed]
            self.visit += item.visit_data[VisitItem.Data.Visited]

    def refresh(self):
        self.calc()
        self.updateText()

    def updateText(self):
        if PercentItem.absolute:
            self.setText(
                "{}{}{}".format(self.visit,
                                '\n' if self.orientation == PercentItem.Orientation.ByLessons else "/",
                                self.total) if self.total != 0 else "0")
            self.setFont(PercentItem.Font.Absolute)
        else:
            self.setText("{}".format(round(self.visit * 100 / self.total) if self.total != 0 else 0))
            self.setFont(PercentItem.Font.Percent)


class PercentHeaderItem(QTableWidgetItem, AbstractContextItem):
    def __init__(self, percents: list, orientation=None, *__args):
        super().__init__(*__args)
        self.percents = percents
        self.mask = "Итого на занятии{}" if orientation != PercentItem.Orientation.ByStudents else "Итого{}"
        self.setText(self.mask.format("" if PercentItem.absolute else ", %"))

    def show_context_menu(self, pos):
        menu = QMenu()
        print(pos)
        menu.move(pos)
        menu.addAction(
            "Отобразить в виде процентов" if PercentItem.absolute else "Отобразить в виде количества",
            self.change(not PercentItem.absolute))
        menu.exec_()

    def change(self, b):
        def f():
            self.setText(self.mask.format("" if b else ", %"))
            PercentItem.absolute = b
            for i in self.percents:
                i.updateText()

        return f


class StudentHeaderItem(QTableWidgetItem, AbstractContextItem):
    def __init__(self, student: dict, *__args):
        super().__init__(*__args)
        if len(student["middle_name"]) > 0:
            self.setText("{} {}. {}.".format(
                student["last_name"],
                student['first_name'][0],
                student["middle_name"][0]
            ))
        else:
            self.setText("{} {}.".format(
                student["last_name"],
                student["first_name"][0]
            ))
        self.student = student

        self.register_process = False

    def show_context_menu(self, pos):
        menu = QMenu()
        print(pos)
        menu.move(pos)
        # if not WorkingData.instance().marking_visits:
        if not self.register_process:
            menu.addAction("Зарегистрировать карту", self._register_student_card)
        else:
            menu.addAction("Отменить регистрацию карты", self.stop_card_register_process)
        menu.addAction("Показать номер карты", lambda: QStatusMessage.instance().setText(self.student["card_id"]))
        menu.exec_()

    def _register_student_card(self):
        QStatusMessage.instance().setText("Приложите карту {} {}.{}. для регистрации".format(
            self.student["last_name"],
            self.student['first_name'][0],
            self.student["middle_name"][0]))
        RFIDReader.instance().onReadOnce(self._register_student_card_onRead)
        self.register_process = True

    def _register_student_card_onRead(self, card_id):
        self.stop_card_register_process()

        DataBaseWorker.instance().add_card_id_to(card_id=card_id, student_id=self.student["id"])

        if self.student["card_id"] is not None:
            QStatusMessage.instance().setText("Студенту {} {} перезаписали номер карты".format(
                self.student["last_name"],
                self.student["first_name"]))
        else:
            QStatusMessage.instance().setText("Студенту {} {} записали номер карты".format(
                self.student["last_name"],
                self.student["first_name"]))

        self.student = DataBaseWorker.instance().get_students(student_id=self.student["id"])[0]

    def stop_card_register_process(self):
        QStatusMessage.instance().setText("Регистрация карты остановлена")
        self.register_process = False
        RFIDReader.instance().remove_temporary_function()
