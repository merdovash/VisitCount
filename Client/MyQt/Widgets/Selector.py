import datetime
from collections import namedtuple

from PyQt5.QtCore import Qt, pyqtSlot, pyqtSignal
from PyQt5.QtWidgets import QWidget, QHBoxLayout, QLabel, QPushButton, QTabWidget, QVBoxLayout

from Client.IProgram import IProgram
from Client.MyQt.Widgets.ComboBox import MComboBox
from Client.MyQt.Widgets.ComboBox.SemesterComboBox import SemesterComboBox, DisciplineComboBox, GroupComboBox, \
    LessonComboBox
from Client.MyQt.Widgets.Table import VisitSection
from DataBase2 import Discipline, Group, Lesson, Professor
from Domain import Data
from Domain.Data import lessons_of


def closest_lesson(lessons: list, date_format="%d-%m-%Y %I:%M%p") -> Lesson:
    """

    :param date_format:
    :param lessons: list of lessons
    :return: closest lesson in list to current datetime
    """
    if len(lessons) == 0:
        return None
    closest = min(
        lessons,
        key=lambda x: abs(datetime.datetime.now() - x.date))
    return closest


CurrentData = namedtuple('CurrentData', 'discipline groups lesson')


class Selector(QWidget):
    set_up = pyqtSignal('PyQt_PyObject')

    semester_changed = pyqtSignal('PyQt_PyObject')
    discipline_changed = pyqtSignal('PyQt_PyObject')  # actual Signature (Discipline)
    group_changed = pyqtSignal('PyQt_PyObject')  # actual signature (List[Group])
    lesson_changed = pyqtSignal('PyQt_PyObject')  # actual signature (Lesson)

    data_changed = pyqtSignal()
    lesson_started = pyqtSignal('PyQt_PyObject')
    lesson_finished = pyqtSignal()

    professor: Professor = None

    def __init__(self, program: IProgram):
        super().__init__()
        self.setObjectName("Selector")

        self.program: IProgram = program
        self.professor = self.program.professor

        main_layout = QVBoxLayout()

        self.tabs = QTabWidget()

        self.table = VisitSection(self)
        self.tabs.addTab(self.table, "Таблица посещений")
        self.tabs.addTab(QWidget(), 'Задания (TODO)')

        selector_layout = QHBoxLayout()

        main_layout.addLayout(selector_layout, stretch=1)
        main_layout.addWidget(self.tabs, stretch=95)

        # semester
        self.semester = SemesterComboBox(self)
        sem_label = QLabel('Семестр')
        sem_label.setAlignment(Qt.AlignRight)

        selector_layout.addWidget(sem_label, 1, alignment=Qt.AlignCenter | Qt.AlignRight)
        selector_layout.addWidget(self.semester, 2)

        # discipline
        self.discipline = DisciplineComboBox(self)
        disc_label = QLabel("Дисциплина")
        disc_label.setAlignment(Qt.AlignRight)

        selector_layout.addWidget(disc_label, 1, alignment=Qt.AlignCenter | Qt.AlignRight)
        selector_layout.addWidget(self.discipline, 2)

        # group
        self.group = GroupComboBox(self)
        self.group.setObjectName('custom-select')
        group_label = QLabel("Группа")
        group_label.setAlignment(Qt.AlignRight)

        selector_layout.addWidget(group_label, 1, alignment=Qt.AlignCenter | Qt.AlignRight)
        selector_layout.addWidget(self.group, 2)

        # lesson
        self.lesson = LessonComboBox(self)
        lesson_label = QLabel("Занятие")
        lesson_label.setAlignment(Qt.AlignRight)

        selector_layout.addWidget(lesson_label, 1,
                                  alignment=Qt.AlignCenter | Qt.AlignRight)
        selector_layout.addWidget(self.lesson, 2)

        self.start_button = QPushButton()
        self.start_button.setText("Начать занятие")

        self.end_button = QPushButton()
        self.end_button.setText("Завершить занятие")
        self.end_button.setVisible(False)

        selector_layout.addWidget(self.end_button, 2)
        selector_layout.addWidget(self.start_button, 2)

        self.setLayout(main_layout)

        selector_layout.setContentsMargins(0, 0, 0, 0)

        self.last_lesson = 0

        self.connect()
        self.semester.init(self.professor)

    def connect(self):
        self.semester.current_changed.connect(self.discipline.on_parent_change)

        self.discipline.current_changed.connect(self.group.on_parent_change)

        self.group.current_changed.connect(self.lesson.on_parent_change)
        self.group.current_changed.connect(self.table.update_data)

        self.lesson.current_changed.connect(self.table.on_lesson_change)
        self.table.horizontalHeader().change_lesson.connect(self.lesson.setCurrent)

        self.start_button.clicked.connect(self.user_start_lesson)
        self.lesson_started.connect(self.start_lesson)
        self.lesson_started.connect(self.table.on_lesson_start)

        self.end_button.clicked.connect(self.user_stop_lesson)
        self.lesson_finished.connect(self.end_lesson)
        self.lesson_finished.connect(self.table.on_lesson_stop)

    @pyqtSlot(int, name='user_change_lesson')
    def user_change_lesson(self, new_lesson_index):
        self.lesson_changed.emit(self.lesson.current())

    @pyqtSlot(bool, name='user_start_lesson')
    def user_start_lesson(self, status):
        self.lesson_started.emit(self.lesson.current())

    @pyqtSlot(name='user_stop_lesson')
    def user_stop_lesson(self):
        self.lesson_finished.emit()

    def update_disciplines(self, semester):
        print('discipline_updated')
        lessons = lessons_of(professor=self.professor, semester=semester)
        current_lesson = closest_lesson(lessons)
        disciplines = Discipline.of(lessons)

        last_discipline_index = self.discipline.currentIndex()

        self.discipline.set_items(disciplines)
        self.discipline.setCurrent(current_lesson.discipline)

        if last_discipline_index == self.discipline.currentIndex() or last_discipline_index == -1:
            self.discipline_changed.emit(self.discipline.current())

    def update_groups(self, discipline):
        lessons = lessons_of(professor=self.professor, discipline=discipline, semester=self.semester.current())
        groups = Group.of(lessons)
        current_lesson = closest_lesson(lessons)

        last_groups_index = self.group.currentIndex()

        self.group.set_items(groups)
        self.group.setCurrent(current_lesson.groups)

        if last_groups_index == self.group.currentIndex() or last_groups_index == -1:
            self.group_changed.emit(self.group.current())

    def update_lessons(self, group):
        lessons = lessons_of(
            professor=self.professor,
            discipline=self.discipline.current(),
            groups=group,
            semester=self.semester.current())

        current_lesson = closest_lesson(lessons)

        self.lesson.set_items(lessons)
        self.lesson.setCurrent(current_lesson)

    def start_lesson(self):
        self.start_button.setVisible(False)
        self.end_button.setVisible(True)

        self.setEnabledControl(False)

        self._is_lesson_started = True

    def end_lesson(self):
        self.start_button.setVisible(True)
        self.end_button.setVisible(False)

        self.setEnabledControl(True)

        self._is_lesson_started = False

    def setEnabledControl(self, b: bool):
        self.lesson.setEnabled(b)
        self.group.setEnabled(b)
        self.discipline.setEnabled(b)

    @pyqtSlot()
    def on_data_change(self):
        self._group_changed(self.group.currentIndex())
