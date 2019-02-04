from typing import Any, Callable, List

from Client.MyQt.Widgets.ComboBox import MComboBox
from DataBase2 import Discipline, Group, Lesson
from Domain.Data import names_of_groups


class SemesterComboBox(MComboBox):
    def extractor(self, item: Lesson)-> Any:
        return item.semester

    def filter_cond(self, semester):
        def cond(lesson: Lesson):
            return lesson.semester == semester
        return cond

    def formatter(self, semester) -> str:
        return str(semester)

    def sorter(self, semester) -> Any:
        return semester

    def __init__(self, parent=None):
        super().__init__(parent, int)

    def init(self, professor):
        self.lessons = Lesson.of(professor)
        self.on_parent_change(self.lessons, None)


class DisciplineComboBox(MComboBox):
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
    def filter_cond(self, group: List[Group]) -> Callable[[Any], bool]:
        def cond(lesson: Lesson):
            return set(lesson.groups) == set(group)
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
            return item==lesson
        return cond

    def extractor(self, lesson: Lesson) -> Any:
        return lesson

    def formatter(self, lesson: Lesson) -> str:
        return lesson.date.strftime("%Y.%m.%d %H:%M")

    def sorter(self, lesson: Lesson) -> Any:
        return lesson.date

    def __init__(self, parent):
        super().__init__(parent, Lesson)
