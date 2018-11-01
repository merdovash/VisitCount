"""
This module contains main Window with tables

TODO:
    * fix error on relogin after changing user
"""
import datetime
from typing import List

from PyQt5.QtCore import Qt, pyqtSlot, pyqtSignal
from PyQt5.QtGui import QFont
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, \
    QLabel, QAction, QMenu

from Client.IProgram import IProgram
from Client.MyQt.Chart.QAnalysisDialog import show
from Client.MyQt.Chart.WeekAnalysis import WeekChart
from Client.MyQt.Chart.WeekDayAnalysis import WeekDayChart
from Client.MyQt.QAction.DataAction import DataAction
from Client.MyQt.QAction.RegisterProfessorCard import RegisterProfessorCard
from Client.MyQt.QtMyStatusBar import QStatusMessage
from Client.MyQt.Table import VisitTable
from Client.MyQt.Window import AbstractWindow
from Client.MyQt.Window.Main.Selector import Selector
from Client.MyQt.Window.NotificationParam import NotificationWindow
from Client.Types import valid_card
from DataBase2 import Professor, Lesson, Visitation, Student
from DataBase2.Types import format_name
from Domain import Action, Prepare
from Domain.Data import find

month_names = "0,Январь,Февраль,Март,Апрель,Май,Июнь,Июль,Август,Сентябрь,Октябрь,Ноябрь,Декабрь".split(
    ',')


def closest_lesson(lessons: List[Lesson]):
    """

    :param lessons: list of lessons
    :return: closest lesson in list to current datetime
    """

    if len(lessons) == 0:
        return None
    closest = min(
        lessons,
        key=lambda x: abs(datetime.datetime.now() - x.date))
    return closest


class MainWindow(AbstractWindow):
    """
    class represents main window in program. includes table, control elements, status info, professor data.
    """

    def __init__(self, program: IProgram, professor: Professor):
        super().__init__()

        self.program: IProgram = program

        self.professor = professor
        if str(professor.id) not in program.win_config:
            program.win_config.new_user(professor.id)
            program.win_config.set_professor_id(professor.id)

        self.c_w = MainWindowWidget(program=program, professor=professor)
        self.setCentralWidget(self.c_w)

        self.__init_menu__()

        self.showMaximized()

    def closeEvent(self, *args, **kwargs):
        self.program.reader().close()

    def __init_menu__(self):
        menu_bar = self.menuBar()

        self.menu_bar = menu_bar

        self._init_menu_file()
        self._init_menu_analysis()
        self._init_menu_view()
        self._init_menu_lessons()
        self._init_menu_updates()
        self._init_notification()

    def _init_menu_analysis(self):
        analysis = self.menu_bar.addMenu("Анализ")

        analysis_weeks = QAction("По неделям", self)
        analysis_weeks.triggered.connect(show(WeekChart, self.program))

        analysis.addAction(analysis_weeks)

        analysis_week_days = QAction("По дням недели", self)
        analysis_week_days.triggered.connect(show(WeekDayChart, self.program))

        analysis.addAction(analysis_week_days)

    def _init_menu_lessons(self):
        lessons = self.menu_bar.addMenu("Занятия")

        lessons_current = QAction("Выбрать ближайщее занятие", self)
        lessons_current.triggered.connect(
            self.centralWidget().selector.select_current_lesson)

        lessons_current_for_group = QAction(
            "Выбрать ближайщее занятие для выбранной группы", self)
        lessons_current_for_group.triggered.connect(
            self.centralWidget().selector.select_current_group_current_lesson)

        lessons.addAction(lessons_current)
        lessons.addAction(lessons_current_for_group)

    def _init_menu_file(self):
        file = self.menu_bar.addMenu("Файл")

        file_change_user = QAction("Сменить пользоватлея", self)
        file_change_user.triggered.connect(lambda: self.program.change_user())

        file.addAction(file_change_user)

        if self.program.professor is not None:
            if not valid_card(self.program.professor.card_id):
                file.addAction(RegisterProfessorCard(self.program, self))

        file_exit = QAction("Выход", self)
        file_exit.triggered.connect(self.close)

        file.addAction(file_exit)

    def _init_menu_view(self):
        view: QMenu = self.menu_bar.addMenu("Вид")

        data = QMenu('Заголовок таблицы')
        view.addMenu(data)

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

        data.addAction(
            DataAction(
                ["Отображать номер недели", "Не отображать номер недели"],
                VisitTable.Header.WEEK_NUMBER,
                self
            )
        )

        view.addSeparator()
        view.addAction('Отображать перекрестие', self.centralWidget().switch_show_table_cross)

    def _init_menu_updates(self):
        updates = self.menu_bar.addMenu("Синхронизация")

        updates_action = QAction("Обновить локальную базу данных", self)
        updates_action.triggered.connect(lambda x: Action.send_updates(self.program.auth.login,
                                                                       self.program.auth.password,
                                                                       self.program.host,
                                                                       ))

        updates.addAction(updates_action)

    def _init_notification(self):
        note = self.menu_bar.addMenu('Оповещения')

        note_run = QAction('Настройка оповещения', self)
        note_run.triggered.connect(
            NotificationWindow(self.professor, self).exec)

        note.addAction(note_run)


class MainWindowWidget(QWidget):
    """
    contains select lesson menu and table
    """
    ready_draw_table = pyqtSignal()

    def __init__(self, program: IProgram, professor: Professor):
        super().__init__()

        self.program: IProgram = program
        self.professor = professor
        self.table = None

        self.last_lesson = None

        self._setup_select_lesson()
        self._setup_geometry()

        # self._setup_data()

        self.start_sync.connect(self.run_synchronization)

    # signals
    start_sync = pyqtSignal()

    # slots
    @pyqtSlot(name='run_synchronization')
    def run_synchronization(self):
        """
        Slot!
        Runs synchronization process
        """

        Action.send_updates(self.program.auth.login,
                            self.program.auth.password,
                            self.program.host,
                            Prepare.updates(self.program.session))
        pass

    def _setup_geometry(self):
        pass

    def _setup_select_lesson(self):
        main_layout = QVBoxLayout()

        # INFO BLOCK
        info_layout = QHBoxLayout()

        professor_label = QLabel(
            format_name(self.professor)
        )
        professor_label.setFont(QFont("", 20))

        self.info_label = QStatusMessage()

        info_layout.addWidget(professor_label, alignment=Qt.AlignLeft)
        info_layout.addWidget(self.info_label, alignment=Qt.AlignRight)

        main_layout.addLayout(info_layout)

        # SELECTOR BLOCK
        self.selector = Selector(self.program)
        self.selector.group_changed.connect(self.on_group_change)
        self.selector.lesson_changed.connect(self.mark_current_lesson)
        self.ready_draw_table.connect(self.selector.on_ready_draw_table)
        self.selector.lesson_started.connect(self._start_lesson)
        self.selector.lesson_finished.connect(self._end_lesson)

        main_layout.addWidget(self.selector)

        # DATA BLOCK
        self.table = VisitTable(main_layout, self.program)
        self.table.show_visitation_msg.connect(self.show_message)

        self.setLayout(main_layout)

        self.ready_draw_table.emit()

    def set_current_lesson(self, lesson=None):
        """
        Select a lesson close to the current time.
        """
        if lesson is None:
            lessons = self.professor.lessons
            closest = closest_lesson(lessons)
            # self.lesson_selector.setCurrentId(getLessonIndex(self.lesson_selector.items, closest))
            self.selector.select_current_lesson(closest)
        else:
            self.selector.select_current_lesson(lesson)

    def set_current_lesson_of_current_group(self):
        """
        Select a lesson close to the current time for the currently selected group.
        """
        lessons = Lesson.filter(professor=self.professor,
                                discipline=self.selector.discipline.current(),
                                group=self.selector.group.current())
        closest = closest_lesson(lessons)
        self.lesson_selector.setCurrent(closest['id'])

    def show_message(self, text, is_red):
        self.info_label.setText(text)
        self.info_label.setStyleSheet(f'color: {"red" if is_red else "black"}')

    def refresh_table(self):
        """
        refill table
        """
        self.table.clear()
        lessons = Lesson.filter(professor=self.professor,
                                discipline=self.selector.discipline.current(),
                                group=self.selector.group.current())

        self.table.set_horizontal_header(lessons)

        self.fill_table()

        self.selector.lesson_selector.disconnect()
        self.selector.lesson_selector.clear()
        self.selector.lesson_selector.addItems(lessons)
        self.selector.lesson_selector.currentIndexChanged.connect(
            self._lesson_changed)
        closest = closest_lesson(lessons)
        # self.lesson_selector.setCurrentId(closest_lesson(lessons)["id"])

        self._lesson_changed()

    @pyqtSlot('PyQt_PyObject', 'PyQt_PyObject',
              name="on_group_change")  # actual signature (int, int)
    def on_group_change(self, discipline, groups):
        professor = self.program.professor

        self.table.clear()
        print(type(groups))
        self.students = Student.of(groups)
        print('students', len(self.students))
        self.lessons = Lesson.filter(self.professor,
                                     self.selector.discipline.current(),
                                     groups)

        self.last_lesson = None

        self.fill_table()

        if self.program.reader() is not None:
            self.program.reader().stop_read()

        self.info_label.setText(
            f"Выбрана группа {groups[0].name}" if len(groups) == 1
            else f'Выбраны группы {",".join([x.name for x in groups])}')

    # @pyqtSlot(int)

    @pyqtSlot('PyQt_PyObject', 'PyQt_PyObject', name="mark_current_lesson")
    def mark_current_lesson(self, column, last_lesson=None):
        assert 0 <= column, f'wrong columns number: columns={column}'
        self.table.visit_table.scrollTo(
            self.table.visit_table.model().index(1, column))

        table: VisitTable = self.table

        if last_lesson is not None and last_lesson > -1:
            for item in table.get_column(last_lesson):
                item.set_current_lesson(False)

        for item in table.get_column(column):
            item.set_current_lesson(True)

    def _lesson_changed(self, qt_index=None):
        index = self.table.lessons.index(
            self.selector.lesson_selector.current())
        self.table.lessons = sorted(self.table.lessons, key=lambda x: x.date)
        self.mark_current_lesson(index)

        self.last_lesson = index
        self.table.visit_table.scrollTo(
            self.table.visit_table.model().index(1, self.last_lesson))

    def fill_table(self):
        """
        fill table with current group students and lessons
        :return: None
        """

        self.table.set_horizontal_header(self.lessons)

        for student in self.students:
            self.table.add_student(student)

        self.table.fill_percents_byStudent()

        return

    @pyqtSlot(int, name='start_lesson')
    def _start_lesson(self, lesson_index):
        lesson = self.table.lessons[lesson_index]
        lesson.completed = True

        column = self.table.get_column(lesson_index)
        for item in column:
            item.update()

        self.program.reader().on_read(self._new_visit)

        self.program.session.flush()
        self.program.session.commit()

    def _new_visit(self, card_id):
        current_data = self.selector.get_current_data()

        student = find(lambda student: student.card_id == card_id,
                       self.students)

        if student is None:
            self.program.window.message.emit("Студента нет в списке.", False)
        else:
            lesson = current_data.lesson

            Visitation.new(student, lesson)

            self.table.new_visit(student, lesson)

    @pyqtSlot(int, name='end_lesson')
    def _end_lesson(self, lesson_index):
        self.start_sync.emit()

    def switch_show_table_cross(self):
        self.table.switch_show_table_cross()
