from itertools import chain
from typing import List

from DataBase2 import Student, Group


def students_of_groups(groups: List[Group]) -> List[Student]:
    return sorted(chain.from_iterable(map(lambda x: x.students, chain(groups))), key=lambda x: x.last_name)


def names_of_groups(groups: List[Group]) -> str:
    return ', '.join(list(map(lambda x: x.name, groups)))


def student_info(student: Student) -> str:
    return f'{student.last_name} {student.first_name} {student.middle_name}, {names_of_groups(student.groups)}'
