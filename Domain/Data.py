from pydoc import locate
from typing import List

from sqlalchemy.ext.associationproxy import _AssociationList

from DataBase2 import Student, Group, Lesson, Visitation, Administration, Discipline, Professor, \
    StudentsGroups, LessonsGroups


def select_by_id(session, mapper, ID):
    assert isinstance(ID, int), f'ID is not a number'
    assert mapper is not None
    if isinstance(mapper, str):
        return select_by_id(session, locate(f'DataBase2.{mapper}'), ID)
    else:
        return session.query(mapper).filter(mapper.id == ID).first()


def valid_card(user):
    assert user is not None, 'user is None'
    assert hasattr(user, 'card_id'), f'object {user} have no card_id'

    return user.card_id is not None and user.card_id != 'None'


def student_info(student: Student) -> str:
    assert student is not None, f'student object {student} is None'

    return f'{student.last_name} {student.first_name} {student.middle_name}, {Group.names(student.groups)}'


def lessons_of(professor, groups=None, discipline=None, semester=None):
    total = Lesson.of(professor)

    if discipline is not None:
        total = [item for item in total if item.discipline == discipline]
    if groups is not None:
        total = [item for item in total if set(item.groups) == set(groups)]
    if semester is not None:
        total = [item for item in total if item.semester == semester]

    return sorted(total, key=lambda x: x.date)
