import datetime

from PyQt5 import QtGui
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont
from PyQt5.QtWidgets import QWidget, QTableWidget, QVBoxLayout, QHBoxLayout, \
    QLabel, QPushButton

from Main import config
from Main.DataBase import sql_handler
from Main.DataBase.SendNew import send
from Main.MyQt.QtMyComboBox import QMyComboBox
from Main.MyQt.QtMyStatusBar import QStatusMessage
from Main.MyQt.QtMyTableWidget import VisitTable
from Main.MyQt.QtMyWidgetItem import VisitItem

month_names = "0,Январь,Февраль,Март,Апрель,Май,Июнь,Июль,Август,Сентябрь,Октябрь,Ноябрь,Декабрь".split(',')


def color_col(col: int, last_col: int, table: QTableWidget):
    for i in range(3, table.rowCount()):
        try:
            table.item(i, col).current_lesson(True)
            table.item(i, last_col).current_lesson(False)
        except Exception as e:
            print(e)


def getLessonIndex(lessons: list, ID: int):
    for i in range(len(lessons)):
        if lessons[i]["id"] == ID:
            return i


def closest_lesson(lessons: list):
    closest = min(
        lessons,
        key=lambda x: abs(datetime.datetime.now() - datetime.datetime.strptime(x["date"], "%d-%m-%Y %I:%M%p")))
    return closest


class QMyMainWindow(QWidget):
    def __init__(self, professor_id, program):
        super().__init__()
        self.program = program

        self.db = sql_handler.DataBaseWorker.get()
        self.professor_id = professor_id
        try:
            self.setup_select_lesson()
            self.setup_geometry()

            self.setup_data()
        except Exception as e:
            print(e)

    def setup_geometry(self):
        self.showMaximized()

    def setup_select_lesson(self):
        self.l = QVBoxLayout()

        # INFO BLOCK
        self.info_layout = QHBoxLayout()

        professor = self.db.get_professors(professor_id=self.professor_id)[0]
        self.professor_label = QLabel(
            professor["last_name"] + " " + professor["first_name"] + " " + professor["middle_name"]
        )
        self.professor_label.setFont(QFont("", 20))

        self.info_label = QStatusMessage.get()

        self.info_layout.addWidget(self.professor_label)
        self.info_layout.addWidget(self.info_label)

        self.l.addLayout(self.info_layout)

        # SELECTOR BLOCK
        self.selector_layout = QHBoxLayout()

        # discipline
        self.discipline_selector = QMyComboBox()
        self.discipline_selector.currentTextChanged.connect(self.discipline_changed)
        disc_label = QLabel("Дисциплина")
        disc_label.setAlignment(Qt.AlignRight)

        self.selector_layout.addWidget(disc_label)
        self.selector_layout.addWidget(self.discipline_selector)

        # group
        self.group_selector = QMyComboBox()
        self.group_selector.currentTextChanged.connect(self.group_changed)
        group_label = QLabel("Группа")
        group_label.setAlignment(Qt.AlignRight)

        self.selector_layout.addWidget(group_label)
        self.selector_layout.addWidget(self.group_selector)

        # lesson
        self.lesson_selector = QMyComboBox("lessons")
        self.lesson_selector.currentTextChanged.connect(self.lesson_changed)
        lesson_label = QLabel("Занятие")
        lesson_label.setAlignment(Qt.AlignRight)

        self.selector_layout.addWidget(lesson_label)
        self.selector_layout.addWidget(self.lesson_selector)

        self.l.addLayout(self.selector_layout)

        # start button
        self.start_button = QPushButton()
        self.start_button.setStyleSheet(config.main_button_css)
        self.start_button.setText("Начать занятие")
        self.start_button.clicked.connect(self.start_lesson)

        self.selector_layout.addWidget(self.start_button)

        # DATA BLOCK
        self.table = VisitTable(self.l)

        # self.l.addWidget(self.table)

        self.setLayout(self.l)

    def resizeEvent(self, a0: QtGui.QResizeEvent):
        self.table.resizeEvent(a0)

    def setup_data(self):
        # disciplines = self.db.get_disciplines(professor_id=self.professor_id)
        # self.discipline_selector.addItems(disciplines)

        try:
            lessons = self.db.get_lessons(professor_id=self.professor_id)
            closest = closest_lesson(lessons)

            disciplines = self.db.get_disciplines(professor_id=self.professor_id)
            self.discipline_selector.disconnect()
            self.discipline_selector.addItems(disciplines)
            self.discipline_selector.currentIndexChanged.connect(self.discipline_changed)

            self.discipline_selector.setCurrentId(closest["discipline_id"])
            self.group_selector.setCurrentId(closest["group_id"])
            self.lesson_selector.setCurrentId(closest["id"])

        except Exception as e:
            print(e)

    def discipline_changed(self):
        """
        update groups ComboBox
        :return: None
        """
        disc = self.discipline_selector.currentId()
        groups = self.db.get_groups(professor_id=self.professor_id, discipline_id=disc)
        self.group_selector.disconnect()
        self.group_selector.clear()
        self.group_selector.currentIndexChanged.connect(self.group_changed)
        self.group_selector.addItems(groups)

    def group_changed(self):
        self.table.clear()
        self.last_lesson = None
        group = self.group_selector.currentId()

        if group is None:
            return

        lessons = self.db.get_lessons(
            professor_id=self.professor_id,
            group_id=group,
            discipline_id=self.discipline_selector.currentId())
        lessons.sort(key=lambda x: datetime.datetime.strptime(x["date"], "%d-%m-%Y %I:%M%p"))

        self.table.set_horizontal_header(lessons)

        self.lesson_selector.disconnect()
        self.lesson_selector.clear()
        self.lesson_selector.addItems(lessons)
        self.lesson_selector.currentTextChanged.connect(self.lesson_changed)
        closest = closest_lesson(lessons)
        print("closest", closest, closest in self.lesson_selector.get_data())
        self.lesson_selector.setCurrentId(closest_lesson(lessons)["id"])
        pass
        self.fill_table()
        self.lesson_changed()

    def lesson_changed(self):
        current_col = getLessonIndex(self.table.lessons, self.lesson_selector.currentId())
        if self.last_lesson is not None:
            self.table.columnForEach(
                self.last_lesson,
                lambda x: x.current_lesson(False) if type(x) is VisitItem else 0)

        self.table.columnForEach(
            current_col,
            lambda x: x.current_lesson(True) if type(x) is VisitItem else 0)

        self.last_lesson = current_col
        self.table.visit_table.scrollTo(self.table.visit_table.model().index(1, self.last_lesson))

    def fill_table(self):
        students = self.db.get_students(
            group_id=self.group_selector.currentId())
        students.sort(key=lambda x: x["last_name"])

        lessons = self.db.get_lessons(
            professor_id=self.professor_id,
            group_id=self.group_selector.currentId(),
            discipline_id=self.discipline_selector.currentId())
        lessons.sort(key=lambda x: datetime.datetime.strptime(x["date"], "%d-%m-%Y %I:%M%p"))

        # self.table.set_horizontal_header(lessons)

        for st in students:
            self.table.add_student(st, self.db.get_visitations(
                student_id=st["id"],
                professor_id=self.professor_id,
                discipline_id=self.discipline_selector.currentId()))
        return

    def start_lesson(self):
        self.lesson_selector.setEnabled(False)
        self.group_selector.setEnabled(False)
        self.discipline_selector.setEnabled(False)

        self.db.start_lesson(lesson_id=self.lesson_selector.currentId())

        try:
            if self.last_lesson is None:
                self.last_lessons = self.table.lessons.index(closest_lesson(self.lesson_selector.get_data()))

            self.start_button.disconnect()
            self.start_button.setText("Завершить занятие")
            self.start_button.clicked.connect(self.end_lesson)
            for i in range(3, self.table.rowCount()):
                if self.table.visit_table.item(i, self.last_lesson).status == VisitItem.Status.NoInfo:
                    self.table.visit_table.item(i, self.last_lesson).set_visit_status(VisitItem.Status.NotVisited)

            self.info_label.setText("Учет начался. Приложите карту студента к считывателю.")
            self.program.serial.method = self.new_visit
        except Exception as e:
            print("start_lesson", e)

    def new_visit(self, ID):
        students = self.db.get_students(card_id=ID, group_id=self.group_selector.currentId())
        if len(students) == 0:
            self.info_label.setText("Студента нет в списках.")
        else:
            student = students[0]
            if ID in [i["card_id"] for i in self.table.students]:
                r = self.db.add_visit(student_id=student["id"], lesson_id=self.lesson_selector.currentId())
                print(r)

                student_table_row = 3 + self.table.students.index(student)
                lesson_table_col = self.last_lesson

                item = self.table.visit_table.item(student_table_row, lesson_table_col)
                if type(item) is VisitItem:
                    if item.status == VisitItem.Status.Visited:
                        self.info_label.setText(
                            "Студент " + student["last_name"] + " " + student["first_name"] + " уже отмечен")
                    else:
                        item.set_visit_status(VisitItem.Status.Visited)
                        # self.db.add_visit(student["id"], self.last_lesson)
                        self.info_label.setText(
                            "Студент " + student["last_name"] + " " + student["first_name"] + " посетил занятие")
                else:
                    print("ERROR: new_visit->update table item ({},{}) is not {}".format(student_table_row,
                                                                                         lesson_table_col,
                                                                                         type(VisitItem)))
                self.table.recalculate_percents(self.table.students.index(student))
                self.table.visit_table.dataChanged(
                    self.table.visit_table.model().index(student_table_row, lesson_table_col),
                    self.table.visit_table.model().index(student_table_row, lesson_table_col))
            else:
                self.info_label.setText(
                    "Студент не из группы "
                    + self.db.get_groups(group_id=self.group_selector.currentId())[0]["name"]
                )

    def end_lesson(self):
        send(self.db, self.professor_id)

        self.program.serial.method = lambda x: 0

        self.lesson_selector.setEnabled(True)
        self.group_selector.setEnabled(True)
        self.discipline_selector.setEnabled(True)

        self.start_button.disconnect()
        self.start_button.setText("Начать занятие")
        self.start_button.clicked.connect(self.start_lesson)
        r = self.db.complete_lesson(self.last_lesson)
        self.table.recalculate_percents()
        self.info_label.setText("Учет посещений завершен.")
        print(r)
