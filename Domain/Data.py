from typing import List

from sqlalchemy.ext.associationproxy import _AssociationList

from DataBase2 import Student, Group, Lesson, Visitation, Administration, Discipline, Professor, NotificationParam, \
    StudentsGroups, LessonsGroups
from Domain.functools.Function import memoize


def valid_card(user):
    assert user is not None, 'user is None'
    assert hasattr(user, 'card_id'), f'object {user} have no card_id'

    return user.card_id is not None and user.card_id != 'None'


def names_of_groups(groups: List[Group]) -> str:
    if isinstance(groups, (list, set, _AssociationList)):
        return ', '.join(list(map(lambda x: x.name, groups)))
    elif isinstance(groups, Group):
        return groups.name
    else:
        raise NotImplementedError(type(groups))


def student_info(student: Student) -> str:
    assert student is not None, f'student object {student} is None'

    return f'{student.last_name} {student.first_name} {student.middle_name}, {names_of_groups(student.groups)}'


def find(func, list_, default=None):
    for item in list_:
        if func(item):
            return item
    return default


@memoize
def lessons_of(professor, groups, discipline):
    discipline_lessons = set(Lesson.of(discipline))
    groups_lessons = set(Lesson.of(groups))
    professor_lessons = set(Lesson.of(professor))

    return sorted(discipline_lessons.intersection(groups_lessons.intersection(professor_lessons)),
                  key=lambda lesson: lesson.date)


def is_exist(base, object_, session):
    if isinstance(object_, Visitation):
        old = session \
            .query(Visitation) \
            .filter(Visitation.lesson_id == object_.lesson_id, Visitation.student_id == Visitation.student_id).first()

        return old is not None, old
    elif isinstance(object_, (Student, Professor, Lesson, Discipline, Group, Administration)):
        old = session.query(base).filter(base.id == object_.id).first()

        return old is not None, old
    elif isinstance(object_, NotificationParam):
        old = session.query(NotificationParam) \
            .filter(NotificationParam.professor_id == object_.professor_id) \
            .filter(NotificationParam.admin_id == object_.admin_id) \
            .first()
        return old is not None, old
    elif isinstance(object_, StudentsGroups):
        old = session.query(StudentsGroups) \
            .filter(StudentsGroups.student_id == object_.student_id, StudentsGroups.group_id == object_.group_id) \
            .first()
        return old is not None, old
    elif isinstance(object_, LessonsGroups):
        old = session.query(LessonsGroups) \
            .filter(LessonsGroups.lesson_id == object_.lesson_id, LessonsGroups.group_id == object_.group_id) \
            .first()
        return old is not None, old
    else:
        raise NotImplementedError(type(object_))
