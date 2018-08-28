"""
This module contains main Window with tables

TODO:
    * fix error on relogin after changing user
"""
import datetime

from PyQt5.QtCore import Qt, pyqtSlot, pyqtSignal
from PyQt5.QtGui import QFont
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, \
    QLabel, QPushButton, QAction

from Client.MyQt.Chart.QAnalysisDialog import show
from Client.MyQt.Chart.WeekAnalysis import WeekChart
from Client.MyQt.Chart.WeekDayAnalysis import WeekDayChart
from Client.MyQt.QAction.DataAction import DataAction
from Client.MyQt.QtMyComboBox import QMyComboBox
from Client.MyQt.QtMyStatusBar import QStatusMessage
from Client.MyQt.Table import VisitTable
from Client.MyQt.Table.Items import VisitItem
from Client.MyQt.Window import AbstractWindow
from Client.Reader import RFIDReader, RFIDReaderNotFoundException
from Client.test import safe
from Modules.Synchronize.ClientSide import Synchronize

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


def closest_lesson(lessons: list, date_format="%d-%m-%Y %I:%M%p"):
    """

    :param date_format:
    :param lessons: list of lessons
    :return: closest lesson in list to current datetime
    """
    if len(lessons) == 0:
        return None
    closest = min(
        lessons,
        key=lambda x: abs(datetime.datetime.now() - datetime.datetime.strptime(x["date"], date_format)))
    return closest


class MainWindow(AbstractWindow):
    """
    class represents main window in program. includes table, control elements, status info, professor data.
    """

    @safe
    def __init__(self, program):
        super().__init__()
        self.program = program
        self.db = program.db

        professor_id = program.auth.get_user_info()['id']
        if str(professor_id) not in program.win_config:
            program.win_config.new_user(professor_id)
            program.win_config.set_professor_id(professor_id)

        self.c_w = MainWindowWidget(program=program)
        self.setCentralWidget(self.c_w)

        self.__init_menu__()

        self.showMaximized()

    # signals

    # slots
    @pyqtSlot()
    def change_user(self):
        self.program.change_user()

    @safe
    def __init_menu__(self):
        menu_bar = self.menuBar()

        self.menu_bar = menu_bar

        self._init_menu_file()
        self._init_menu_analysis()
        self._init_menu_data()
        self._init_menu_lessons()
        self._init_menu_updates()

    @safe
    def _init_menu_analysis(self):
        analysis = self.menu_bar.addMenu("Анализ")

        analysis_weeks = QAction("По неделям", self)
        analysis_weeks.triggered.connect(show(WeekChart, self.program))

        analysis.addAction(analysis_weeks)

        analysis_week_days = QAction("По дням недели", self)
        analysis_week_days.triggered.connect(show(WeekDayChart, self.program))

        analysis.addAction(analysis_week_days)

    @safe
    def _init_menu_lessons(self):
        lessons = self.menu_bar.addMenu("Занятия")

        lessons_current = QAction("Выбрать текущее", self)
        lessons_current.triggered.connect(self.centralWidget()._setup_data)

        lessons_current_for_group = QAction("Выбрать текущее для группы", self)
        lessons_current_for_group.triggered.connect(self.centralWidget().set_current_lesson_of_current_group)

        lessons.addAction(lessons_current)
        lessons.addAction(lessons_current_for_group)

    @safe
    def _init_menu_file(self):
        file = self.menu_bar.addMenu("Файл")

        file_change_user = QAction("Сменить пользоватлея", self)
        file_change_user.triggered.connect(self.change_user)

        file.addAction(file_change_user)

        file_exit = QAction("Выход", self)
        file_exit.triggered.connect(self.close)

        file.addAction(file_exit)

    @safe
    def _init_menu_data(self):
        data = self.menu_bar.addMenu("Данные")

        data_show_month_day = DataAction(
            ["Отображать день", "Не отображать день"],
            VisitTable.Header.DAY,
            self
        )
        data.addAction(data_show_month_day)

        data.addAction(
            DataAction(
                ["Отображать день недели", "Не отображать день недели"],
                VisitTable.Header.WEEKDAY,
                self
            )
        )
        data.addAction(
            DataAction(
                ["Отображать месяц", "Не отображать месяц"],
                VisitTable.Header.MONTH,
                self
            )
        )
        data.addAction(
            DataAction(
                ["Отображать номер занятия", "Не отображать номер занятия"],
                VisitTable.Header.LESSON,
                self
            )
        )
        data.addAction(
            DataAction(
                ["Отображать тип занятия", "Не отображать тип занятия"],
                VisitTable.Header.LESSONTYPE,
                self
            )
        )

    @safe
    def _init_menu_updates(self):
        updates = self.menu_bar.addMenu("Синхронизация")

        updates_action = QAction("Обновить локальную базу данных", self)
        updates_action.triggered.connect(Synchronize(self.program).start)

        updates.addAction(updates_action)


class MainWindowWidget(QWidget):
    """
    contains select lesson menu and table
    """

    @safe
    def __init__(self, program):
        super().__init__()

        self.program = program
        self.table = None

        self.last_lesson = None

        self.program['professor'] = program.auth.get_user_info()

        self._setup_select_lesson()
        self._setup_geometry()

        self._setup_data()

        self.synchronize = Synchronize(self.program)
        self.start_sync.connect(self.run_synchonization)

    # signals
    start_sync = pyqtSignal()

    # slots
    @pyqtSlot()
    def run_synchonization(self):
        self.synchronize._run()

    @safe
    def _setup_geometry(self):
        pass

    @safe
    def _setup_select_lesson(self):
        main_layout = QVBoxLayout()

        # INFO BLOCK
        info_layout = QHBoxLayout()

        professor = self.program.auth.get_user_info()
        professor_label = QLabel(
            professor["last_name"] + " " + professor["first_name"] + " " + professor["middle_name"]
        )
        professor_label.setFont(QFont("", 20))

        self.info_label = QStatusMessage()

        info_layout.addWidget(professor_label, alignment=Qt.AlignLeft)
        info_layout.addWidget(self.info_label, alignment=Qt.AlignRight)

        main_layout.addLayout(info_layout)

        # SELECTOR BLOCK
        selector_layout = QHBoxLayout()

        # discipline
        self.discipline_selector = QMyComboBox()
        self.discipline_selector.currentIndexChanged.connect(self.discipline_changed)
        disc_label = QLabel("Дисциплина")
        disc_label.setAlignment(Qt.AlignRight)

        selector_layout.addWidget(disc_label, alignment=Qt.AlignCenter)
        selector_layout.addWidget(self.discipline_selector, alignment=Qt.AlignCenter)

        # group
        self.group_selector = QMyComboBox()
        self.group_selector.currentIndexChanged.connect(self._group_changed)
        group_label = QLabel("Группа")
        group_label.setAlignment(Qt.AlignRight)

        selector_layout.addWidget(group_label)
        selector_layout.addWidget(self.group_selector)

        # lesson
        self.lesson_selector = QMyComboBox("lessons")
        self.lesson_selector.currentIndexChanged.connect(self._lesson_changed)
        lesson_label = QLabel("Занятие")
        lesson_label.setAlignment(Qt.AlignRight)

        selector_layout.addWidget(lesson_label)
        selector_layout.addWidget(self.lesson_selector)

        main_layout.addLayout(selector_layout)

        # start button
        self.start_button = QPushButton()
        self.start_button.setStyleSheet(self.program.db.config.main_button_css)
        self.start_button.setText("Начать занятие")
        self.start_button.clicked.connect(self._start_lesson)

        selector_layout.addWidget(self.start_button)

        # DATA BLOCK
        self.table = VisitTable(main_layout, self.program)
        self.table.show_visitation_msg.connect(self.show_message)

        self.setLayout(main_layout)

    def set_current_lesson(self):
        """
        Select a lesson close to the current time.
        """
        lessons = self.program.db.get_lessons(professor_id=self.program['professor']["id"])
        closest = closest_lesson(lessons, self.program['date_format'])
        # self.lesson_selector.setCurrentId(getLessonIndex(self.lesson_selector.items, closest))
        self.program['lesson'] = closest

    def set_current_lesson_of_current_group(self):
        """
        Select a lesson close to the current time for the currently selected group.
        """
        lessons = self.program.db.get_lessons(professor_id=self.program['professor']["id"],
                                              group_id=self.program['group']['id'])
        closest = closest_lesson(lessons, self.program['date_format'])
        self.lesson_selector.setCurrentId(closest['id'])

    def show_message(self, text):
        self.info_label.setText(text)

    @safe
    def _setup_data(self, *args):
        self.set_current_lesson()

        disciplines = self.program.db.get_disciplines(professor_id=self.program['professor']["id"])
        self.discipline_selector.disconnect()
        self.discipline_selector.clear()
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
    @safe
    def discipline_changed(self, qt_index=None):
        """
        update groups ComboBox
        :return: None
        """
        discipline_id = self.discipline_selector.currentId()
        self.program['discipline'] = self.program.db.get_disciplines(discipline_id=discipline_id)[0]

        groups = self.program.db.get_groups(
            professor_id=self.program['professor']["id"],
            discipline_id=discipline_id)

        self.group_selector.disconnect()
        self.group_selector.clear()
        self.group_selector.addItems(groups)
        self.group_selector.currentIndexChanged.connect(self._group_changed)

        pass

    @safe
    def refresh_table(self):
        """
        refill table
        """
        self.table.clear()
        lessons = self.program.db.get_lessons(
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
        closest = closest_lesson(lessons, self.program['date_format'])
        print("closest", closest, closest in self.lesson_selector.get_data())
        # self.lesson_selector.setCurrentId(closest_lesson(lessons)["id"])

        self._lesson_changed()

    # @pyqtSlot(int)
    @safe
    def _group_changed(self, qt_index=None):
        self.table.clear()
        self.last_lesson = None
        group = self.group_selector.currentId()

        self.program['group'] = self.program.db.get_groups(group_id=group)[0]

        if group is None:
            return

        lessons = self.program.db.get_lessons(
            professor_id=self.program['professor']["id"],
            group_id=group,
            discipline_id=self.discipline_selector.currentId())
        print(self.program["professor"], lessons)
        lessons.sort(key=lambda x: datetime.datetime.strptime(x["date"], self.program['date_format']))

        self.table.set_horizontal_header(lessons)

        self.lesson_selector.disconnect()
        self.lesson_selector.clear()
        self.lesson_selector.addItems(lessons)
        self.lesson_selector.currentIndexChanged.connect(self._lesson_changed)

        # self.lesson_selector.setCurrentId(self.program['lesson']['id'])

        self.fill_table()
        self._lesson_changed()

        try:
            RFIDReader.instance().stopRead()
        except RFIDReaderNotFoundException:
            pass
        self.info_label.setText("Выбрана группа {}".format(self.group_selector.currentText()))

    # @pyqtSlot(int)
    @safe
    def _lesson_changed(self, qt_index=None):

        @safe
        def select_current_col(col):
            print(f'colorfull {col}')

            table: VisitTable = self.table

            if self.last_lesson is not None:
                for item in table.get_column(self.last_lesson):
                    item.set_current_lesson(False)

            for item in table.get_column(col):
                item.set_current_lesson(True)

        current_col = getLessonIndex(self.table.lessons, self.lesson_selector.currentId())
        select_current_col(current_col)

        self.last_lesson = current_col
        self.table.visit_table.scrollTo(self.table.visit_table.model().index(1, self.last_lesson))

        self.program['lesson'] = self.program.db.get_lessons(
            lesson_id=self.lesson_selector.currentId())[0]

    @safe
    def fill_table(self):
        """
        fill table with current group students and lessons
        :return: None
        """
        students = self.program.db.get_students(
            group_id=self.group_selector.currentId())
        students.sort(key=lambda x: x["last_name"])

        lessons = self.program.db.get_lessons(
            professor_id=self.program['professor']["id"],
            group_id=self.group_selector.currentId(),
            discipline_id=self.discipline_selector.currentId())
        lessons.sort(key=lambda x: datetime.datetime.strptime(x["date"], self.program['date_format']))

        # self.table.set_horizontal_header(lessons)

        print(students)

        for student in students:
            self.table.add_student(student, self.program.db.get_visitations(
                student_id=student["id"],
                professor_id=self.program['professor']["id"],
                discipline_id=self.discipline_selector.currentId()))

        self.table.fill_percents_byStudent()

        return

    # @pyqtSlot(bool)
    @safe
    def _start_lesson(self, qt_bool):
        if self.program.reader() is not None:
            self.program.reader().onRead(self._new_visit)

            self.program['marking_visits'] = True
            self.lesson_selector.setEnabled(False)
            self.group_selector.setEnabled(False)
            self.discipline_selector.setEnabled(False)

            self.program.db.start_lesson(lesson_id=self.lesson_selector.currentId())

            if self.last_lesson is None:
                self.last_lessons = self.table.lessons.index(closest_lesson(self.lesson_selector.get_data(),
                                                                            self.program['date_format']))

            self.start_button.disconnect()
            self.start_button.setText("Завершить занятие")
            self.start_button.clicked.connect(self._end_lesson)
            for i in range(3, self.table.rowCount()):
                item = self.table.visit_table.item(i, self.last_lesson)
                if isinstance(item, VisitItem.VisitItem):
                    if item.status == VisitItem.VisitItem.Status.NoInfo:
                        item.set_visit_status(VisitItem.VisitItem.Status.NotVisited)

            self.program.window.message.emit("Учет начался. Приложите карту студента к считывателю.")
        else:
            self.program.window.error.emit("Для учета посещений необходимо подключение считывателя.")

    @safe
    def _new_visit(self, card_id):
        students = self.program.db.get_students(card_id=card_id, group_id=self.group_selector.currentId())
        if len(students) == 0:
            self.info_label.setText("Студента нет в списках.")
        else:
            lesson_id = self.lesson_selector.currentId()
            student = students[0]
            if card_id in [i["card_id"] for i in self.table.students]:
                self.program.db.add_visit(
                    student_id=student["id"],
                    lesson_id=lesson_id)

                self.table.new_visit(student["id"], lesson_id)
            else:
                self.info_label.setText("Студент не из группы {}".format(
                    self.program.db.get_groups(group_id=self.group_selector.currentId())[0]["name"])
                )

    @pyqtSlot()
    @safe
    def _end_lesson(self, *qt_args):
        self.program['marking_visits'] = False

        self.start_sync.emit()

        self.program.reader().stopRead()

        self.lesson_selector.setEnabled(True)
        self.group_selector.setEnabled(True)
        self.discipline_selector.setEnabled(True)

        self.start_button.disconnect()
        self.start_button.setText("Начать занятие")
        self.start_button.clicked.connect(self._start_lesson)
        if self.last_lesson is not None:
            self.program.db.complete_lesson(self.last_lesson)
            self.info_label.setText("Учет посещений завершен.")