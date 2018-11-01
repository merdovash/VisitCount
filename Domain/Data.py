from typing import List

from DataBase2 import Student, Group


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
