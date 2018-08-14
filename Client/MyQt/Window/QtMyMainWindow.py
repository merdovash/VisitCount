import datetime
import os
import sys

from PyQt5.QtCore import Qt, pyqtSlot
from PyQt5.QtGui import QFont
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, \
    QLabel, QPushButton, QApplication, QAction, QMainWindow

import Client.Configuartion.WindowConfig as WindowConfig
from Client.MyQt.QAction.DataAction import DataAction
from Client.MyQt.QtMyComboBox import QMyComboBox
from Client.MyQt.QtMyStatusBar import QStatusMessage
from Client.MyQt.QtMyTableWidget import VisitTable
from Client.MyQt.QtMyWidgetItem import VisitItem
from Client.MyQt.Window.Chart.QAnalysisDialog import show, QAnalysisDialog
from Client.MyQt.Window.Chart.WeekAnalysis import WeekChart
from Client.MyQt.Window.Chart.WeekDayAnalysis import WeekDayChart
from Client.Requests.SendNew import SendNewVisitation
from Client.Requests.Synchronize import Synchronize
from Client.SerialsReader import RFIDReader, nothing, RFIDReaderNotFoundException
from Client.test import try_except
from DataBase.Authentication import Authentication

month_names = "0,Январь,Февраль,Март,Апрель,Май,Июнь,Июль,Август,Сентябрь,Октябрь,Ноябрь,Декабрь".split(',')


def getLessonIndex(lessons: list, lesson_id: int) -> int:
    """

    :param lessons: list of lessons
    :param lesson_id: id of lessons that needs to find
    :return: index of lesson in list
    """
    for i in range(len(lessons)):
        if lessons[i]["id"] == lesson_id:
            return i


def closest_lesson(lessons: list):
    """

    :param lessons: list of lessons
    :return: closest lesson in list to current datetime
    """
    closest = min(
        lessons,
        key=lambda x: abs(datetime.datetime.now() - datetime.datetime.strptime(x["date"], "%d-%m-%Y %I:%M%p")))
    return closest


class MainWindow(QMainWindow):
    """
    class represents main window in program. includes table, control elements, status info, professor data.
    """

    @try_except
    def __init__(self, auth: Authentication, program: 'MyProgram',
                 window_config: WindowConfig.Config):
        super().__init__()
        self.program = program
        self.db = program.db
        self.auth = auth

        self.win_config = window_config
        professor_id = auth.get_user_info()['id']
        if str(professor_id) not in window_config:
            window_config.new_user(professor_id)
        window_config.set_professor_id(professor_id)

        self.c_w = MainWindowWidget(self.auth, program=program, window_config=self.win_config)
        self.setCentralWidget(self.c_w)

        self.__init_menu__()
        self.dialog = None

        self.showMaximized()

    @try_except
    def __init_menu__(self):
        bar = self.menuBar()

        self.bar = bar

        self._init_menu_file()
        self._init_menu_analysis()
        self._init_menu_data()
        self._init_menu_lessons()
        self._init_menu_updates()

    @try_except
    def _init_menu_analysis(self):
        analysis = self.bar.addMenu("Анализ")

        analysis_weeks = QAction("По неделям", self)
        analysis_weeks.triggered.connect(show(WeekChart, self))

        analysis.addAction(analysis_weeks)

        analysis_week_days = QAction("По дням недели", self)
        analysis_week_days.triggered.connect(show(WeekDayChart, self))

        analysis.addAction(analysis_week_days)

    @try_except
    def _init_menu_lessons(self):
        lessons = self.bar.addMenu("Занятия")

        lessons_current = QAction("Выбрать текущее", self)
        lessons_current.triggered.connect(self.centralWidget()._setup_data)

        lessons.addAction(lessons_current)

    @try_except
    def _init_menu_file(self):
        file = self.bar.addMenu("Файл")

        file_change_user = QAction("Сменить пользоватлея", self)
        file_change_user.triggered.connect(self.program.change_user)

        file.addAction(file_change_user)

        file_exit = QAction("Выход", self)
        file_exit.triggered.connect(self.close)

        file.addAction(file_exit)

    @try_except
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

    @try_except
    def _init_menu_updates(self):
        updates = self.bar.addMenu("Синхронизация")

        updates_action = QAction("Обновить локальную базу данных", self)
        updates_action.triggered.connect(Synchronize(self.db, self.program['professor']['id']).run)

        updates.addAction(updates_action)

    @try_except
    def setDialog(self, dialog: QAnalysisDialog):
        """

        :param dialog: QAnalysisDialog that contains graph to show
        """
        self.dialog = dialog
        self.dialog.show()


class MainWindowWidget(QWidget):
    """
    contains select lesson menu and table
    """

    @try_except
    def __init__(self, auth: Authentication, program: 'MyProgram',
                 window_config: WindowConfig.Config):
        super().__init__()
        self.program = program
        self.table = None
        self.auth = auth
        self.db = program.db
        self.window_config = window_config

        self.last_lesson = None
        self.dialog = None

        self.program['professor'] = auth.get_user_info()

        self._setup_select_lesson()
        self._setup_geometry()

        self._setup_data()

    @try_except
    def _setup_geometry(self):
        pass

    @try_except
    def _setup_select_lesson(self):
        self.main_layout = QVBoxLayout()

        # INFO BLOCK
        self.info_layout = QHBoxLayout()

        professor = self.auth.get_user_info()
        self.professor_label = QLabel(
            professor["last_name"] + " " + professor["first_name"] + " " + professor["middle_name"]
        )
        self.professor_label.setFont(QFont("", 20))

        self.info_label = QStatusMessage.instance()

        self.info_layout.addWidget(self.professor_label)
        self.info_layout.addWidget(self.info_label)

        self.main_layout.addLayout(self.info_layout)

        # SELECTOR BLOCK
        self.selector_layout = QHBoxLayout()

        # discipline
        self.discipline_selector = QMyComboBox()
        self.discipline_selector.currentIndexChanged.connect(self.discipline_changed)
        disc_label = QLabel("Дисциплина")
        disc_label.setAlignment(Qt.AlignRight)

        self.selector_layout.addWidget(disc_label, alignment=Qt.AlignCenter)
        self.selector_layout.addWidget(self.discipline_selector, alignment=Qt.AlignCenter)

        # group
        self.group_selector = QMyComboBox()
        self.group_selector.currentIndexChanged.connect(self._group_changed)
        group_label = QLabel("Группа")
        group_label.setAlignment(Qt.AlignRight)

        self.selector_layout.addWidget(group_label)
        self.selector_layout.addWidget(self.group_selector)

        # lesson
        self.lesson_selector = QMyComboBox("lessons")
        self.lesson_selector.currentIndexChanged.connect(self._lesson_changed)
        lesson_label = QLabel("Занятие")
        lesson_label.setAlignment(Qt.AlignRight)

        self.selector_layout.addWidget(lesson_label)
        self.selector_layout.addWidget(self.lesson_selector)

        self.main_layout.addLayout(self.selector_layout)

        # start button
        self.start_button = QPushButton()
        self.start_button.setStyleSheet(self.db.config.main_button_css)
        self.start_button.setText("Начать занятие")
        self.start_button.clicked.connect(self._start_lesson)

        self.selector_layout.addWidget(self.start_button)

        # DATA BLOCK
        print("#####", self.window_config)
        self.table = VisitTable(self.main_layout, self.program, self.window_config)
        # self.setCentralWidget(self.table)

        # self.inner_layout.addWidget(self.table)

        self.setLayout(self.main_layout)

    def _set_current_lesson(self):
        lessons = self.db.get_lessons(professor_id=self.program['professor']["id"])
        closest = closest_lesson(lessons)
        self.program['lesson'] = closest

    def _set_current_group_lesson(self):
        lessons = self.db.get_lessons(professor_id=self.program['professor']["id"],
                                      group_id=self.program['group']['id'])
        closest = closest_lesson(lessons)
        self.lesson_selector.setCurrentId(closest['id'])

    @try_except
    def _setup_data(self, *args):
        self._set_current_lesson()

        disciplines = self.db.get_disciplines(professor_id=self.program['professor']["id"])
        self.discipline_selector.disconnect()
        self.discipline_selector.addItems(disciplines)
        self.discipline_selector.currentIndexChanged.connect(self.discipline_changed)

        if len(disciplines) <= 2:
            self.discipline_changed()
        else:
            self.discipline_selector.setCurrentId(self.program['lesson']["discipline_id"])

        if self.group_selector.currentId() == self.program['lesson']['group_id']:
            self.group_selector.currentIndexChanged.emit()
        else:
            self.group_selector.setCurrentId(self.program['lesson']["group_id"])

        self.lesson_selector.setCurrentId(self.program['lesson']["id"])

    # @pyqtSlot(int)
    @try_except
    def discipline_changed(self, index=None):
        """
        update groups ComboBox
        :return: None
        """
        discipline_id = self.discipline_selector.currentId()
        self.program['discipline'] = self.db.get_disciplines(discipline_id=discipline_id)[0]

        groups = self.db.get_groups(
            professor_id=self.program['professor']["id"],
            discipline_id=discipline_id)

        self.group_selector.disconnect()
        self.group_selector.clear()
        self.group_selector.addItems(groups)
        self.group_selector.currentIndexChanged.connect(self._group_changed)

        pass

    @try_except
    def refresh_table(self):
        """
        refill table
        """
        self.table.clear()
        lessons = self.db.get_lessons(
            professor_id=self.program['professor']["id"],
            group_id=self.program['group']["id"],
            discipline_id=self.program['discipline']["id"])
        lessons.sort(key=lambda x: datetime.datetime.strptime(x["date"], "%d-%m-%Y %I:%M%p"))

        self.table.set_horizontal_header(lessons)

        self.fill_table()

        self.lesson_selector.disconnect()
        self.lesson_selector.clear()
        self.lesson_selector.addItems(lessons)
        self.lesson_selector.currentIndexChanged.connect(self._lesson_changed)
        closest = closest_lesson(lessons)
        print("closest", closest, closest in self.lesson_selector.get_data())
        # self.lesson_selector.setCurrentId(closest_lesson(lessons)["id"])

        self._lesson_changed()

    # @pyqtSlot(int)
    @try_except
    def _group_changed(self, index=None):
        self.table.clear()
        self.last_lesson = None
        group = self.group_selector.currentId()

        self.program['group'] = self.db.get_groups(group_id=group)[0]

        if group is None:
            return

        lessons = self.db.get_lessons(
            professor_id=self.program['professor']["id"],
            group_id=group,
            discipline_id=self.discipline_selector.currentId())
        print(self.program["professor"], lessons)
        lessons.sort(key=lambda x: datetime.datetime.strptime(x["date"], "%d-%m-%Y %I:%M%p"))

        self.table.set_horizontal_header(lessons)

        self.lesson_selector.disconnect()
        self.lesson_selector.clear()
        self.lesson_selector.addItems(lessons)
        self.lesson_selector.currentIndexChanged.connect(self._lesson_changed)

        self.lesson_selector.setCurrentId(self.program['lesson']['id'])

        self.fill_table()
        self._lesson_changed()

        try:
            RFIDReader.instance().method = nothing
        except RFIDReaderNotFoundException:
            pass
        QStatusMessage.instance().setText("Выбрана группа {}".format(self.group_selector.currentText()))

    # @pyqtSlot(int)
    @try_except
    def _lesson_changed(self, index=None):

        def select_current_col(col):
            if self.last_lesson is not None:
                self.table.ForEachRow(
                    self.last_lesson,
                    lambda x: x.set_current_lesson(False) if type(x) is VisitItem else 0)

            self.table.ForEachRow(
                current_col,
                lambda x: x.set_current_lesson(True) if type(x) is VisitItem else 0)

        current_col = getLessonIndex(self.table.lessons, self.lesson_selector.currentId())
        select_current_col(current_col)

        self.last_lesson = current_col
        self.table.visit_table.scrollTo(self.table.visit_table.model().index(1, self.last_lesson))

        self.program['lesson'] = self.db.get_lessons(
            lesson_id=self.lesson_selector.currentId())[0]

    @try_except
    def fill_table(self):
        """
        fill table with current group students and lessons
        :return: None
        """
        students = self.db.get_students(
            group_id=self.group_selector.currentId())
        students.sort(key=lambda x: x["last_name"])

        lessons = self.db.get_lessons(
            professor_id=self.program['professor']["id"],
            group_id=self.group_selector.currentId(),
            discipline_id=self.discipline_selector.currentId())
        lessons.sort(key=lambda x: datetime.datetime.strptime(x["date"], "%d-%m-%Y %I:%M%p"))

        # self.table.set_horizontal_header(lessons)

        print(students)

        for st in students:
            self.table.add_student(st, self.db.get_visitations(
                student_id=st["id"],
                professor_id=self.program['professor']["id"],
                discipline_id=self.discipline_selector.currentId()))

        self.table.fill_percents_byStudent()

        return

    @pyqtSlot(bool)
    @try_except
    def _start_lesson(self, b):
        self.program['marking_visits'] = True
        self.lesson_selector.setEnabled(False)
        self.group_selector.setEnabled(False)
        self.discipline_selector.setEnabled(False)

        self.db.start_lesson(lesson_id=self.lesson_selector.currentId())

        if self.last_lesson is None:
            self.last_lessons = self.table.lessons.index(closest_lesson(self.lesson_selector.get_data()))

        self.start_button.disconnect()
        self.start_button.setText("Завершить занятие")
        self.start_button.clicked.connect(self._end_lesson)
        for i in range(3, self.table.rowCount()):
            item = self.table.visit_table.item(i, self.last_lesson)
            if type(item) == VisitItem:
                if item.status == VisitItem.Status.NoInfo:
                    item.set_visit_status(VisitItem.Status.NotVisited)

        QStatusMessage.instance().setText("Учет начался. Приложите карту студента к считывателю.")
        RFIDReader.instance().onRead = self._new_visit

    @try_except
    def _new_visit(self, ID):
        students = self.db.get_students(card_id=ID, group_id=self.group_selector.currentId())
        if len(students) == 0:
            self.info_label.setText("Студента нет в списках.")
        else:
            lesson_id = self.lesson_selector.currentId()
            student = students[0]
            if ID in [i["card_id"] for i in self.table.students]:
                r = self.db.add_visit(student_id=student["id"], lesson_id=lesson_id)
                print(r)

                self.table._new_visit(student["id"], lesson_id)
            else:
                self.info_label.setText(
                    "Студент не из группы "
                    + self.db.get_groups(group_id=self.group_selector.currentId())[0]["name"]
                )

    @pyqtSlot()
    @try_except
    def _end_lesson(self):
        self.program['marking_visits'] = False
        SendNewVisitation(self.db, self.auth).run()

        RFIDReader.instance().method = nothing

        self.lesson_selector.setEnabled(True)
        self.group_selector.setEnabled(True)
        self.discipline_selector.setEnabled(True)

        self.start_button.disconnect()
        self.start_button.setText("Начать занятие")
        self.start_button.clicked.connect(self._start_lesson)
        if self.last_lesson is not None:
            r = self.db.complete_lesson(self.last_lesson)
            self.info_label.setText("Учет посещений завершен.")
            print(r)


if __name__ == "__main__":
    from Client.main import MyProgram

    app = QApplication(sys.argv)
    os.environ["QT_QUICK_CONTROLS_STYLE"] = "Flat Style"
    app.setApplicationName("СПбГУТ - Учет посещений")

    window_config = WindowConfig.load()

    program = MyProgram()
    program.auth_success(1)

    sys.exit(app.exec_())
