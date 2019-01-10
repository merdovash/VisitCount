import datetime
from collections import namedtuple

from PyQt5.QtCore import Qt, pyqtSlot, pyqtSignal
from PyQt5.QtWidgets import QWidget, QHBoxLayout, QLabel, QPushButton, QTabWidget, QVBoxLayout

from Client.IProgram import IProgram
from Client.MyQt.Widgets.ComboBox import MComboBox
from Client.MyQt.Widgets.Table import VisitSection
from DataBase2 import Discipline, Group, Lesson
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
    discipline_changed = pyqtSignal('PyQt_PyObject')  # actual Signature (Discipline)
    group_changed = pyqtSignal('PyQt_PyObject')  # actual signature (List[Group])
    lesson_changed = pyqtSignal('PyQt_PyObject')  # actual signature (Lesson)

    data_changed = pyqtSignal()
    lesson_started = pyqtSignal('PyQt_PyObject')
    lesson_finished = pyqtSignal()

    def __init__(self, program: IProgram):
        super().__init__()
        self.setObjectName("Selector")

        self.program: IProgram = program
        self.professor = program.professor

        main_layout = QVBoxLayout()

        self.tabs = QTabWidget()

        self.table = VisitSection(self.program)
        self.tabs.addTab(self.table, "Таблица посещений")
        self.tabs.addTab(QWidget(), 'Задания (TODO)')

        selector_layout = QHBoxLayout()

        main_layout.addLayout(selector_layout, stretch=1)
        main_layout.addWidget(self.tabs, stretch=95)

        # semester
        self.semester = MComboBox(int)
        self.semester.currentIndexChanged.connect(self.on_semester_changed)
        sem_label = QLabel('Семестр')
        sem_label.setAlignment(Qt.AlignRight)

        selector_layout.addWidget(sem_label, 1, alignment=Qt.AlignCenter | Qt.AlignRight)
        selector_layout.addWidget(self.semester, 2)

        # discipline
        self.discipline = MComboBox(Discipline)
        self.discipline.currentIndexChanged.connect(self._discipline_changed)
        disc_label = QLabel("Дисциплина")
        disc_label.setAlignment(Qt.AlignRight)

        selector_layout.addWidget(disc_label, 1,
                                  alignment=Qt.AlignCenter | Qt.AlignRight)
        selector_layout.addWidget(self.discipline, 2)

        # group
        self.group = MComboBox(Group)
        self.group.setObjectName('custom-select')
        self.group.currentIndexChanged.connect(self._group_changed)
        group_label = QLabel("Группа")
        group_label.setAlignment(Qt.AlignRight)

        selector_layout.addWidget(group_label, 1,
                                  alignment=Qt.AlignCenter | Qt.AlignRight)
        selector_layout.addWidget(self.group, 2)

        # lesson
        self.lesson = MComboBox(Lesson)
        self.lesson.currentIndexChanged.connect(self._lesson_changed)
        lesson_label = QLabel("Занятие")
        lesson_label.setAlignment(Qt.AlignRight)

        selector_layout.addWidget(lesson_label, 1,
                                  alignment=Qt.AlignCenter | Qt.AlignRight)
        selector_layout.addWidget(self.lesson, 2)

        self.start_button = QPushButton()
        self.start_button.setText("Начать занятие")
        self.start_button.setObjectName("start-lesson")
        self.start_button.clicked.connect(self._start_lesson)

        selector_layout.addWidget(self.start_button, 2)

        self.setLayout(main_layout)

        selector_layout.setContentsMargins(0, 0, 0, 0)

        self.last_lesson = 0

        semesters = list(set([o.semester for o in Lesson.of(self.professor)]))
        print(semesters)
        self.semester.addItems(semesters)

    def on_semester_changed(self, new_semester_index):
        lessons = lessons_of(professor=self.professor, semester=self.semester.current())
        disciplines = Discipline.of(lessons)

        self.discipline.blockSignals(True)
        self.discipline.clear()
        self.discipline.addItems(disciplines)
        self.discipline.blockSignals(False)

        self.table.set_semester(self.semester.current())

        self.discipline.currentIndexChanged.emit(0)

    def _discipline_changed(self, new_discipline_index):
        print('discipline_changed')

        professor = self.program.professor

        lessons = Data.lessons_of(
            professor=professor,
            discipline=self.discipline.current(),
            semester=self.semester.current())

        self.table.set_dicipline(self.discipline.current())

        groups = Group.of(lessons)
        print(groups)

        current_lesson = closest_lesson(professor.lessons,
                                        self.program['date_format'])

        current_group = current_lesson.groups

        self.group.set_items(groups)

        index_before = self.group.currentIndex()
        self.group.setCurrent(current_group)
        if self.group.currentIndex() == index_before:
            self._group_changed(self.group.currentIndex())

        self.discipline_changed.emit(self.discipline.current())

    @pyqtSlot(int, name='_group_changed')
    def _group_changed(self, new_group_index):
        self.last_lesson = None
        print('group_changed', new_group_index)
        professor = self.program.professor
        groups = self.group.current()
        discipline = self.discipline.current()

        lessons = Data.lessons_of(
            professor=self.professor,
            discipline=discipline,
            groups=groups,
            semester=self.semester.current()
        )
        current_semester = self.semester.current()
        lessons = list(filter(lambda x: x.semester == current_semester, lessons))
        assert len(lessons) > 0, lessons

        current_lesson = closest_lesson(lessons, self.program['date_format'])

        start_index = self.lesson.currentIndex() if self.lesson.currentIndex() >= 0 else 0

        self.table.clear()
        self.table.set_group(self.group.current())

        self.lesson.blockSignals(True)
        self.lesson.clear()
        self.lesson.addItems(lessons)
        self.lesson.blockSignals(False)
        self.lesson.setCurrent(current_lesson)

        if self.lesson.currentIndex() == start_index:
            self._lesson_changed(self.lesson.currentIndex())

        # self.group_changed.emit(groups)

    def _lesson_changed(self, new_index=None):
        column = new_index
        if column != -1:
            self.lesson_changed.emit(self.lesson.current())

        self.last_lesson = column

    @pyqtSlot()
    def select_current_lesson(self, lesson=None):
        try:
            if lesson is None:
                lesson = closest_lesson(
                    self.professor.lessons,
                    self.program['date_format']
                )

            self.discipline.setCurrent(lesson.discipline)
            self.group.setCurrent(set(lesson.groups))
            self.lesson.setCurrent(lesson)
        except IndexError:
            self.lesson.clear()
            self.lesson.addItems(lessons_of(lesson.professor, lesson.groups, lesson.discipline))

            self.select_current_lesson(lesson)

        # current_data = self.get_current_data()
        # self.group_changed.emit(current_data.discipline_id, current_data.group_id)
        # self.lesson_changed.emit(self.lesson_selector.currentIndex(), self.last_lesson)

    @pyqtSlot()
    def select_current_group_current_lesson(self):
        lessons = list(self.lesson.items.values())
        current_lesson = closest_lesson(lessons, self.program['date_format'])
        self.lesson.setCurrent(current_lesson)

    def start(self):
        lessons = Lesson.of(self.professor)
        lesson = closest_lesson(lessons)

        self.discipline.addItems(Discipline.of(self.professor))

        self.discipline.setCurrent(Discipline.of(lesson)[0])
        self.group.setCurrent(Group.of(lesson))
        self.lesson.setCurrent(lesson)

    def _start_lesson(self, lesson_index):
        self.lesson_started.emit(self.lesson.current())

    def _end_lesson(self):
        self.lesson_finished.emit()

    def switchBtnAction(self, b):
        if not b:
            self.start_button.disconnect()
            self.start_button.setText("Завершить занятие")
            self.start_button.clicked.connect(self._end_lesson)
        else:
            self.start_button.disconnect()
            self.start_button.setText("Начать занятие")
            self.start_button.clicked.connect(self._start_lesson)

    def setEnabledControl(self, b: bool):
        self.lesson.setEnabled(b)
        self.group.setEnabled(b)
        self.discipline.setEnabled(b)

    @pyqtSlot()
    def on_data_change(self):
        self._group_changed(self.group.currentIndex())

    def get_current_data(self):
        return CurrentData(
            self.discipline.current(),
            self.group.current(),
            self.lesson.current()
        )
