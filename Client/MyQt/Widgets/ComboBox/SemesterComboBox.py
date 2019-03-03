from datetime import datetime
from typing import Any, Callable, List

from PyQt5.QtCore import pyqtSlot

from Client.MyQt.Widgets.ComboBox import MComboBox, T
from DataBase2 import Discipline, Group, Lesson, Student, Professor
from Domain.Data import names_of_groups
from Domain.functools.List import closest_lesson


class SemesterComboBox(MComboBox):
    def extractor(self, item: Lesson) -> Any:
        return item.semester

    def filter_cond(self, semester):
        def cond(lesson: Lesson):
            return lesson.semester == semester

        return cond

    def formatter(self, semester) -> str:
        return semester.full_name()

    def sorter(self, semester) -> Any:
        return semester.start_date

    def __init__(self, parent=None):
        super().__init__(parent, int)

    def init(self, professor):
        self.lessons = Lesson.of(professor)
        self.on_parent_change(self.lessons, None)


class DisciplineComboBox(MComboBox):
    label = "Дисциплина"
    def filter_cond(self, discipline: Discipline) -> Callable[[Any], bool]:
        def cond(lesson: Lesson):
            return lesson.discipline_id == discipline.id

        return cond

    def extractor(self, lesson: Lesson) -> Any:
        return lesson.discipline

    def formatter(self, discipline: Discipline) -> str:
        return discipline.name

    def sorter(self, discipline: Discipline) -> Any:
        return discipline.name

    def __init__(self, parent):
        super().__init__(parent, Discipline)


class GroupComboBox(MComboBox):
    label = "Группа"

    def filter_cond(self, group: List[Group]) -> Callable[[Any], bool]:
        def cond(lesson: Lesson) -> bool:
            if len(group) == 1:
                return bool(len(set(lesson.groups) & set(group)))
            if len(group) > 1:
                return set(lesson.groups) == set(group)
            raise ValueError('no groups found')

        return cond

    def extractor(self, lesson: Lesson) -> Any:
        return frozenset(lesson.groups)

    def formatter(self, groups: List[Group]) -> str:
        return names_of_groups(groups)

    def sorter(self, groups: List[Group]) -> Any:
        return f"{len(groups)}{names_of_groups(groups)}"

    def __init__(self, parent):
        super().__init__(parent, Group)


class LessonComboBox(MComboBox):
    def filter_cond(self, lesson) -> Callable[[Any], bool]:
        def cond(item):
            return item == lesson

        return cond

    def extractor(self, lesson: Lesson) -> Any:
        return lesson

    def formatter(self, lesson: Lesson) -> str:
        return lesson.date.strftime("%Y.%m.%d %H:%M")

    def sorter(self, lesson: Lesson) -> Any:
        return lesson.date

    def __init__(self, parent):
        super().__init__(parent, Lesson)


class StudentComboBox(MComboBox):
    @pyqtSlot('PyQt_PyObject', 'PyQt_PyObject', name='on_parent_change')
    def on_parent_change(self, lessons, parent_value):
        self.lessons = lessons

        data = list(set(Student.of(lessons)) & set(Student.of(parent_value)))
        self.set_items(data)
        self.setCurrentIndex(0)

    def extractor(self, item: Lesson) -> Any:
        return Student.of(item, sort=lambda x: x.full_name())

    def formatter(self, item: Student) -> str:
        return item.full_name()

    def sorter(self, item: List[Student]) -> Any:
        return str(sub_item.full_name() for sub_item in item)

    def filter_cond(self, student: Student):
        def cond(lesson):
            return student in Student.of(lesson)

        return cond

    def __init__(self, parent):
        super().__init__(parent, Student)


class ProfessorComboBox(MComboBox):
    T = Professor

    def filter_cond(self, item: T) -> Callable[[Lesson], bool]:
        def cond(lesson: Lesson):
            return lesson.professor == item
        return cond

    def extractor(self, item: Lesson) -> T:
        return item.professor

    def formatter(self, item: T) -> str:
        return item.full_name()

    def sorter(self, item: T) -> Any:
        return item.full_name()

    def __init__(self, parent=None):
        super().__init__(parent, Professor)
