import datetime
import os
import sys
import traceback

from PyQt5 import QtGui
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, \
    QLabel, QPushButton, QApplication, QAction, QMainWindow

from Main import config
import Main.Configuartion.WindowConfig as WindowConfig
from Main.DataBase import sql_handler
from Main.DataBase.SendNew import send
from Main.DataBase.sql_handler import DataBaseWorker
from Main.MyQt.QAction.DataAction import DataAction
from Main.MyQt.QtMyComboBox import QMyComboBox
from Main.MyQt.QtMyStatusBar import QStatusMessage
from Main.MyQt.QtMyTableWidget import VisitTable
from Main.MyQt.QtMyWidgetItem import VisitItem
from Main.MyQt.Window.Chart.QAnalysisDialog import show, QAnalysisDialog
from Main.MyQt.Window.Chart.WeekAnalysis import WeekChart
from Main.MyQt.Window.Chart.WeekDayAnalysis import WeekDayChart
from Main.SerialsReader import RFIDReader, nothing, RFIDReaderNotFoundException
from Main.Types import WorkingData

month_names = "0,Январь,Февраль,Март,Апрель,Май,Июнь,Июль,Август,Сентябрь,Октябрь,Ноябрь,Декабрь".split(',')


def getLessonIndex(lessons: list, ID: int):
    for i in range(len(lessons)):
        if lessons[i]["id"] == ID:
            return i


def closest_lesson(lessons: list):
    closest = min(
        lessons,
        key=lambda x: abs(datetime.datetime.now() - datetime.datetime.strptime(x["date"], "%d-%m-%Y %I:%M%p")))
    return closest


class MainWindow(QMainWindow):
    def __init__(self, professor_id: int or str, program: 'MyProgram', window_config: WindowConfig.Config):
        super().__init__()
        self.config = self.__init_setting__(window_config, professor_id)

        self.program = program

        self.c_w = MainWindowWidget(professor_id, program, self.config)
        self.setCentralWidget(self.c_w)

        print(self.centralWidget())
        self.__init_menu__()
        self.dialog = None

        self.showMaximized()

    def __init_setting__(self, window_config: WindowConfig.Config, professor_id: int) -> WindowConfig.Config:
        c = window_config
        if str(professor_id) not in window_config:
            c.new_user(professor_id)
        c.set_professor(professor_id)

        return c

    def __init_menu__(self):
        bar = self.menuBar()

        self.bar = bar

        self._init_menu_file()

        analysis = bar.addMenu("Анализ")
        analysis_weeks = QAction("По неделям", self)
        analysis_weeks.triggered.connect(show(WeekChart, self))
        analysis.addAction(analysis_weeks)

        analysis_week_days = QAction("По дням недели", self)
        analysis_week_days.triggered.connect(show(WeekDayChart, self))
        analysis.addAction(analysis_week_days)

        self._init_menu_data()

    def _init_menu_file(self):
        file = self.bar.addMenu("Файл")

        file_change_user = QAction("Сменить пользоватлея", self)
        file_change_user.triggered.connect(self.program.change_user)

        file.addAction(file_change_user)

        file_exit = QAction("Выход", self)
        file_exit.triggered.connect(self.close)

        file.addAction(file_exit)

    def _init_menu_data(self):
        data = self.bar.addMenu("Данные")

        d1 = DataAction(["Отображать день", "Не отображать день"], VisitTable.Header.DAY, self)
        data.addAction(d1)

        data.addAction(
            DataAction(["Отображать день недели", "Не отображать день недели"], VisitTable.Header.WEEKDAY, self))
        data.addAction(
            DataAction(["Отображать месяц", "Не отображать месяц"], VisitTable.Header.MONTH, self))
        data.addAction(
            DataAction(["Отображать номер занятия", "Не отображать номер занятия"], VisitTable.Header.LESSON, self))
        data.addAction(
            DataAction(["Отображать тип занятия", "Не отображать тип занятия"], VisitTable.Header.LESSONTYPE, self))

    def setDialog(self, dialog: QAnalysisDialog):
        self.dialog = dialog
        self.dialog.show()


class MainWindowWidget(QWidget):
    def __init__(self, professor_id, program: 'MyProgram', window_config: WindowConfig.Config):
        super().__init__()
        self.table = None

        self.window_config = window_config
        # self.program = program

        self.db = sql_handler.DataBaseWorker.instance()

        print(DataBaseWorker.instance().get_professors())
        WorkingData.instance().professor = DataBaseWorker.instance().get_professors(professor_id=professor_id)[0]
        try:
            self.setup_select_lesson()
            self.setup_geometry()

            self.setup_data()

            self.dialog = None
        except Exception as e:
            traceback.print_exc()

    def show_header(self, i):
        self.table.visit_table.setRowHidden(i, True)

    def setup_geometry(self):
        pass

    def setup_select_lesson(self):
        self.l = QVBoxLayout()

        # INFO BLOCK
        self.info_layout = QHBoxLayout()

        professor = WorkingData.instance().professor
        self.professor_label = QLabel(
            professor["last_name"] + " " + professor["first_name"] + " " + professor["middle_name"]
        )
        self.professor_label.setFont(QFont("", 20))

        self.info_label = QStatusMessage.instance()

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

        self.selector_layout.addWidget(disc_label, alignment=Qt.AlignCenter)
        self.selector_layout.addWidget(self.discipline_selector, alignment=Qt.AlignCenter)

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

        self.table = VisitTable(self.l, self, self.window_config)
        # self.setCentralWidget(self.table)

        # self.inner_layout.addWidget(self.table)

        self.setLayout(self.l)

    def setup_data(self):
        try:
            lessons = self.db.get_lessons(professor_id=WorkingData.instance().professor["id"])
            closest = closest_lesson(lessons)

            disciplines = self.db.get_disciplines(professor_id=WorkingData.instance().professor["id"])
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
        groups = self.db.get_groups(professor_id=WorkingData.instance().professor["id"], discipline_id=disc)
        self.group_selector.disconnect()
        self.group_selector.clear()
        self.group_selector.currentIndexChanged.connect(self.group_changed)
        self.group_selector.addItems(groups)

        WorkingData.instance().discipline = DataBaseWorker.instance().get_disciplines(discipline_id=disc)[0]

    def refresh_table(self):
        self.table.clear()
        lessons = DataBaseWorker.instance().get_lessons(
            professor_id=WorkingData.instance().professor["id"],
            group_id=WorkingData.instance().group["id"],
            discipline_id=WorkingData.instance().discipline["id"])
        lessons.sort(key=lambda x: datetime.datetime.strptime(x["date"], "%d-%m-%Y %I:%M%p"))

        self.table.set_horizontal_header(lessons)

        self.fill_table()

        self.lesson_selector.disconnect()
        self.lesson_selector.clear()
        self.lesson_selector.addItems(lessons)
        self.lesson_selector.currentTextChanged.connect(self.lesson_changed)
        closest = closest_lesson(lessons)
        print("closest", closest, closest in self.lesson_selector.get_data())
        self.lesson_selector.setCurrentId(closest_lesson(lessons)["id"])

        self.lesson_changed()

    def group_changed(self):
        self.table.clear()
        self.last_lesson = None
        group = self.group_selector.currentId()

        WorkingData.instance().group = DataBaseWorker.instance().get_groups(group_id=group)[0]

        if group is None:
            return

        lessons = self.db.get_lessons(
            professor_id=WorkingData.instance().professor["id"],
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

        try:
            RFIDReader.instance().method = nothing
        except RFIDReaderNotFoundException:
            pass
        QStatusMessage.instance().setText("Выбрана группа {}".format(self.group_selector.currentText()))

    def lesson_changed(self):
        current_col = getLessonIndex(self.table.lessons, self.lesson_selector.currentId())
        if self.last_lesson is not None:
            self.table.ForEachRow(
                self.last_lesson,
                lambda x: x.current_lesson(False) if type(x) is VisitItem else 0)

        self.table.ForEachRow(
            current_col,
            lambda x: x.current_lesson(True) if type(x) is VisitItem else 0)

        self.last_lesson = current_col
        self.table.visit_table.scrollTo(self.table.visit_table.model().index(1, self.last_lesson))

        WorkingData.instance().lesson = DataBaseWorker.instance().get_lessons(
            lesson_id=self.lesson_selector.currentId())[0]

    def fill_table(self):
        students = self.db.get_students(
            group_id=self.group_selector.currentId())
        students.sort(key=lambda x: x["last_name"])

        lessons = self.db.get_lessons(
            professor_id=WorkingData.instance().professor["id"],
            group_id=self.group_selector.currentId(),
            discipline_id=self.discipline_selector.currentId())
        lessons.sort(key=lambda x: datetime.datetime.strptime(x["date"], "%d-%m-%Y %I:%M%p"))

        # self.table.set_horizontal_header(lessons)

        for st in students:
            self.table.add_student(st, self.db.get_visitations(
                student_id=st["id"],
                professor_id=WorkingData.instance().professor["id"],
                discipline_id=self.discipline_selector.currentId()))

        self.table.fill_percents_byStudent()

        return

    def start_lesson(self):
        WorkingData.instance().marking_visits = True
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
                item = self.table.visit_table.item(i, self.last_lesson)
                if type(item) == VisitItem:
                    if item.status == VisitItem.Status.NoInfo:
                        item.set_visit_status(VisitItem.Status.NotVisited)

            QStatusMessage.instance().setText("Учет начался. Приложите карту студента к считывателю.")
            RFIDReader.instance().onRead = self.new_visit
        except Exception as e:
            print("start_lesson", e)

    def new_visit(self, ID):
        try:
            students = self.db.get_students(card_id=ID, group_id=self.group_selector.currentId())
            if len(students) == 0:
                self.info_label.setText("Студента нет в списках.")
            else:
                lesson_id = self.lesson_selector.currentId()
                student = students[0]
                if ID in [i["card_id"] for i in self.table.students]:
                    r = self.db.add_visit(student_id=student["id"], lesson_id=lesson_id)
                    print(r)

                    self.table.new_visit(student["id"], lesson_id)
                else:
                    self.info_label.setText(
                        "Студент не из группы "
                        + self.db.get_groups(group_id=self.group_selector.currentId())[0]["name"]
                    )
        except Exception as e:
            print(e)

    def end_lesson(self):
        WorkingData.instance().marking_visits = False
        try:
            send(self.db, WorkingData.instance().professor["id"])

            RFIDReader.instance().method = nothing

            self.lesson_selector.setEnabled(True)
            self.group_selector.setEnabled(True)
            self.discipline_selector.setEnabled(True)

            self.start_button.disconnect()
            self.start_button.setText("Начать занятие")
            self.start_button.clicked.connect(self.start_lesson)
            r = self.db.complete_lesson(self.last_lesson)
            self.info_label.setText("Учет посещений завершен.")
            print(r)
        except Exception as e:
            print(e)


if __name__ == "__main__":
    from Main.main import MyProgram

    app = QApplication(sys.argv)
    os.environ["QT_QUICK_CONTROLS_STYLE"] = "Flat Style"
    app.setApplicationName("СПбГУТ - Учет посещений")

    window_config = WindowConfig.load()

    program = MyProgram()
    program.auth_success(2)

    sys.exit(app.exec_())
