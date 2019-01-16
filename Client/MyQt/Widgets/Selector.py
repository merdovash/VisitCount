from collections import namedtuple

from PyQt5.QtCore import Qt, pyqtSlot, pyqtSignal
from PyQt5.QtWidgets import QWidget, QHBoxLayout, QLabel, QPushButton, QTabWidget, QVBoxLayout

from Client.IProgram import IProgram
from Client.MyQt.Widgets.ComboBox.SemesterComboBox import SemesterComboBox, DisciplineComboBox, GroupComboBox, \
    LessonComboBox
from Client.MyQt.Widgets.TableView import VisitTableWidget
from DataBase2 import Professor

CurrentData = namedtuple('CurrentData', 'discipline groups lesson')


class Selector(QWidget):
    reader_required = pyqtSignal('PyQt_PyObject')

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

        self.table = VisitTableWidget(self)
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
        self.group.current_changed.connect(self.table.setData)

        self.lesson.current_changed.connect(self.table.set_current_lesson)
        self.table.select_current_lesson.connect(self.lesson.setCurrent)

        self.start_button.clicked.connect(self.user_start_lesson)
        self.lesson_started.connect(self.start_lesson)
        self.lesson_started.connect(self.table.on_lesson_start)

        self.end_button.clicked.connect(self.user_stop_lesson)
        self.lesson_finished.connect(self.end_lesson)
        self.lesson_finished.connect(self.table.on_lesson_stop)

    @pyqtSlot(bool, name='user_start_lesson')
    def user_start_lesson(self, status):
        if self.program.reader() is not None:
            self.lesson_started.emit(self.lesson.current())
        else:
            self.reader_required.emit('Считыватель не обнаружен.')

    @pyqtSlot(name='user_stop_lesson')
    def user_stop_lesson(self):
        self.lesson_finished.emit()

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
