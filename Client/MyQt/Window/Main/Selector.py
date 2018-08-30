import datetime
from collections import namedtuple

from PyQt5.QtCore import Qt, pyqtSlot, pyqtSignal
from PyQt5.QtWidgets import QWidget, QHBoxLayout, QLabel, QPushButton

from Client.MyQt.QtMyComboBox import QMyComboBox
from Client.test import safe


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


CurrentData = namedtuple('CurrentData', 'discipline_id group_id lesson_id')


class Selector(QWidget):
    group_changed = pyqtSignal('PyQt_PyObject', 'PyQt_PyObject')  # actual signature (int, int)
    lesson_changed = pyqtSignal('PyQt_PyObject', 'PyQt_PyObject')  # actual signature (int, int)
    data_changed = pyqtSignal()
    lesson_started = pyqtSignal(int)
    lesson_finished = pyqtSignal(int)

    def __init__(self, program):
        super().__init__()

        self.program = program

        selector_layout = QHBoxLayout()

        # discipline
        self.discipline_selector = QMyComboBox()
        self.discipline_selector.currentIndexChanged.connect(self._discipline_changed)
        disc_label = QLabel("Дисциплина")
        disc_label.setAlignment(Qt.AlignRight)

        selector_layout.addWidget(disc_label, 1, alignment=Qt.AlignCenter | Qt.AlignRight)
        selector_layout.addWidget(self.discipline_selector, 2)

        # group
        self.group_selector = QMyComboBox()
        self.group_selector.currentIndexChanged.connect(self._group_changed)
        group_label = QLabel("Группа")
        group_label.setAlignment(Qt.AlignRight)

        selector_layout.addWidget(group_label, 1, alignment=Qt.AlignCenter | Qt.AlignRight)
        selector_layout.addWidget(self.group_selector, 2)

        # lesson
        self.lesson_selector = QMyComboBox("lessons")
        self.lesson_selector.currentIndexChanged.connect(self._lesson_changed)
        lesson_label = QLabel("Занятие")
        lesson_label.setAlignment(Qt.AlignRight)

        selector_layout.addWidget(lesson_label, 1, alignment=Qt.AlignCenter | Qt.AlignRight)
        selector_layout.addWidget(self.lesson_selector, 2)

        self.start_button = QPushButton()
        self.start_button.setStyleSheet(self.program.db.config.main_button_css)
        self.start_button.setText("Начать занятие")
        self.start_button.clicked.connect(self._start_lesson)

        selector_layout.addWidget(self.start_button, 2)

        self.setLayout(selector_layout)

        selector_layout.setContentsMargins(0, 0, 0, 0)

        self.last_lesson = 0

        self.load_data()

    def load_data(self):
        self.discipline_selector.addItems(
            self.program.db.get_disciplines(self.program['professor']['id'])
        )

    @pyqtSlot()
    def on_ready_draw_table(self):
        self.group_changed.emit(self.discipline_selector.currentId(),
                                self.group_selector.currentId())
        self._lesson_changed(self.lesson_selector.currentIndex())

    # @pyqtSlot(int)
    @safe
    def _discipline_changed(self, new_discipline_index):
        print('discipline_changed')
        discipline_id = self.discipline_selector.currentId()

        professor_id = self.program['professor']['id']

        groups = self.program.db.get_groups(professor_id=professor_id,
                                            discipline_id=discipline_id)

        lesson = closest_lesson(self.program.db.get_lessons(professor_id=professor_id,
                                                            discipline_id=discipline_id),
                                self.program['date_format'])

        group_id = lesson['group_id']

        self.group_selector.blockSignals(True)
        self.group_selector.clear()
        self.group_selector.addItems(groups)
        self.group_selector.blockSignals(False)
        self.group_selector.setCurrentMyId(group_id)

    @pyqtSlot(int)
    def _group_changed(self, new_group_index):
        print('group_changed', new_group_index)
        professor_id = self.program['professor']['id']
        group_id = self.group_selector.currentId()
        discipline_id = self.discipline_selector.currentId()

        self.group_changed.emit(discipline_id, group_id)

        lessons = self.program.db.get_lessons(professor_id=professor_id,
                                              group_id=group_id,
                                              discipline_id=discipline_id)
        lessons.sort(key=lambda x: datetime.datetime.strptime(x["date"], self.program['date_format']))

        lesson = closest_lesson(lessons, self.program['date_format'])
        lesson_id = lesson['id']

        start_index = self.lesson_selector.currentIndex()
        self.lesson_selector.blockSignals(True)
        self.lesson_selector.clear()
        self.lesson_selector.addItems(lessons)
        self.lesson_selector.blockSignals(False)
        self.lesson_selector.setCurrentMyId(lesson_id)
        if self.lesson_selector.currentIndex() == start_index:
            self._lesson_changed(self.lesson_selector.currentIndex())

    def _lesson_changed(self, new_index=None):
        column = new_index

        self.lesson_changed.emit(column, self.last_lesson)
        self.last_lesson = column

    @pyqtSlot()
    @safe
    def select_current_lesson(self):
        lesson = closest_lesson(
            self.program.db.get_lessons(professor_id=self.program['professor']['id']),
            self.program['date_format']
        )

        self.discipline_selector.setCurrentMyId(lesson['discipline_id'])
        self.group_selector.setCurrentMyId(lesson['group_id'])
        self.lesson_selector.setCurrentMyId(lesson['id'])

        # current_data = self.get_current_data()
        # self.group_changed.emit(current_data.discipline_id, current_data.group_id)
        # self.lesson_changed.emit(self.lesson_selector.currentIndex(), self.last_lesson)

    @pyqtSlot()
    def select_current_group_current_lesson(self):
        lessons = self.program.db.get_lessons(professor_id=self.program['professor']["id"],
                                              group_id=self.group_selector.currentId())
        closest = closest_lesson(lessons, self.program['date_format'])
        self.lesson_selector.setCurrentMyId(closest['id'])

    @safe
    def _start_lesson(self, lesson_index):
        if self.program.reader() is not None:
            self.lesson_started.emit(self.lesson_selector.currentIndex())

            self.program.db.complete_lesson(lesson_id=self.lesson_selector.currentId(),
                                            professor_id=self.program['professor']['id'])

            self.program['marking_visits'] = True
            self.lesson_selector.setEnabled(False)
            self.group_selector.setEnabled(False)
            self.discipline_selector.setEnabled(False)

            if self.last_lesson is None:
                self.last_lesson = self.table.lessons.index(closest_lesson(self.lesson_selector.get_data(),
                                                                           self.program['date_format']))

            self.start_button.disconnect()
            self.start_button.setText("Завершить занятие")
            self.start_button.clicked.connect(self._end_lesson)

            self.program.window.message.emit("Учет начался. Приложите карту студента к считывателю.")
        else:
            self.program.window.error.emit("Для учета посещений необходимо подключение считывателя.")

    @safe
    def _end_lesson(self, lesson_index):
        print('hello')
        if self.program.reader() is not None:
            self.program.reader().stop_read()
        else:
            self.program.window.error.emit('Во время учета было потеряно соединение со считывателем. Учет завершен.')

        self.program['marking_visits'] = False
        self.lesson_selector.setEnabled(True)
        self.group_selector.setEnabled(True)
        self.discipline_selector.setEnabled(True)

        # change button behavior
        self.start_button.disconnect()
        self.start_button.setText("Начать занятие")
        self.start_button.clicked.connect(self._start_lesson)

        # if self.last_lesson is not None:
        self.program.window.message.emit("Учет посещений завершен.")
        self.lesson_finished.emit(self.lesson_selector.currentIndex())

    @pyqtSlot()
    def on_data_change(self):
        self._group_changed(self.group_selector.currentIndex())

    def get_current_data(self):
        return CurrentData(
            self.discipline_selector.currentId(),
            self.group_selector.currentId(),
            self.lesson_selector.currentId()
        )
