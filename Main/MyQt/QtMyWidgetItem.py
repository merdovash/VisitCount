import PyQt5

from PyQt5.QtCore import Qt, QPoint
from PyQt5.QtGui import QColor, QFont
from PyQt5.QtWidgets import QTableWidgetItem, QMenu

from Main.MyQt.QtMyStatusBar import QStatusMessage
from Main.SerialsReader import RFIDReader, nothing
from Main.DataBase.sql_handler import DataBaseWorker
from Main.Types import WorkingData


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


class VisitItem(MyTableItem):
    class Status(int):
        Visited = 1
        NoInfo = 2
        NotVisited = 0

    class Data(int):
        Completed = 1
        Visited = 0

    def __init__(self, status: Status, student: dict = None, lesson: dict = None):
        super().__init__()
        self.setTextAlignment(Qt.AlignCenter)
        self.status = status
        self.visit_data = [0, 0]
        self.update()

        self.student = student
        self.lesson = lesson

    def set_visit_status(self, status: Status):
        if self.status == status:
            return
        elif (self.status == VisitItem.Status.NotVisited and status == VisitItem.Status.Visited) \
                or (self.status == VisitItem.Status.NoInfo and status == VisitItem.Status.NotVisited):
            self.status = status
            self.update()

    def update(self):
        if self.status == VisitItem.Status.Visited:
            self.setText("+")
            self.color = "#ffff00"
            self.setBackground(self.current_lesson_color if self.current else QColor(self.color))
            self.visit_data = [1, 1]
        elif self.status == VisitItem.Status.NotVisited:
            self.setText("-")
            self.setBackground(self.current_lesson_color if self.current else QColor(self.color))
            self.visit_data = [0, 1]
        elif self.status == VisitItem.Status.NoInfo:
            self.setText("")
            self.setBackground(self.current_lesson_color if self.current else QColor(self.color))
            self.visit_data = [0, 0]

    def show_context_menu(self, pos):
        if self.status == VisitItem.Status.NotVisited and not WorkingData.instance().marking_visits:
            menu = QMenu()
            print(pos)
            menu.move(pos)
            menu.addAction("Отметить посещение", self._set_visited_by_professor)
            menu.exec_()

    def _set_visited_by_professor(self):
        print(WorkingData.instance().professor)
        QStatusMessage.instance().setText("Приложите карточку преподавателя для подтверждения")
        RFIDReader.instance().method = self._set_visited_by_professor_onReadCard

    def _set_visited_by_professor_onReadCard(self, card_id):
        if int(card_id) == int(WorkingData.instance().professor["card_id"]):
            self.status = VisitItem.Status.Visited
            QStatusMessage.instance().setText("Подтвеждено")
        else:
            QStatusMessage.instance().setText("Ошибка")
        RFIDReader.instance().method = nothing


class LessonTypeItem(QTableWidgetItem):
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
        if not WorkingData.instance().marking_visits:
            menu = QMenu()
            print(pos)
            menu.move(pos)
            menu.addAction("Начать учет", )
            menu.exec_()


month_names = "0,Январь,Февраль,Март,Апрель,Май,Июнь,Июль,Август,Сентябрь,Октябрь,Ноябрь,Декабрь".split(',')


class MonthTableItem(QTableWidgetItem):
    def __init__(self, month: int):
        super().__init__()
        self.setTextAlignment(Qt.AlignCenter)
        self.setText(month_names[month])


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


class PercentHeaderItem(QTableWidgetItem):
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


class StudentHeaderItem(QTableWidgetItem):
    def __init__(self, student: dict, *__args):
        super().__init__(*__args)
        self.setText("{} {}. {}.".format(
            student["last_name"],
            student['first_name'][0],
            student["middle_name"][0]
        ))
        self.student = student

        self.register_process = False

    def show_context_menu(self, pos):
        menu = QMenu()
        print(pos)
        menu.move(pos)
        if not self.register_process:
            menu.addAction("Зарегистрировать карту", self.register)
        else:
            menu.addAction("Отменить регистрацию карты", self.stop_card_register_process)
        menu.addAction("Показать номер карты", lambda: QStatusMessage.instance().setText(self.student["card_id"]))
        menu.exec_()

    def register(self):
        QStatusMessage.instance().setText("Приложите карту {} {}.{}. для регистрации".format(
            self.student["last_name"],
            self.student['first_name'][0],
            self.student["middle_name"][0]))
        RFIDReader.instance().method = self.reader_handler
        self.register_process = True

    def reader_handler(self, card_id):
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
        RFIDReader.instance().method = nothing
