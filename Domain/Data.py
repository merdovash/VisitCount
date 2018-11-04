from typing import List

from DataBase2 import Student, Group, Lesson
from Domain.functools.Function import memoize


def valid_card(user):
    assert user is not None, 'user is None'
    assert hasattr(user, 'card_id'), f'object {user} have no card_id'

    return user.card_id is not None and user.card_id != 'None'


def names_of_groups(groups: List[Group]) -> str:
    return ', '.join(list(map(lambda x: x.name, groups)))


def student_info(student: Student) -> str:
    assert student is not None, f'student object {student} is None'

    return f'{student.last_name} {student.first_name} {student.middle_name}, {names_of_groups(student.groups)}'


def find(func, list_, default=None):
    for item in list_:
        if func(item):
            return item
    return default


@memoize
def lessons(professor, groups, discipline):
    discipline_lessons = set(Lesson.of(discipline))
    groups_lessons = set(Lesson.of(groups))
    professor_lessons = set(Lesson.of(professor))

    return sorted(discipline_lessons.intersection(groups_lessons.intersection(professor_lessons)),
                  key=lambda lesson: lesson.date)
