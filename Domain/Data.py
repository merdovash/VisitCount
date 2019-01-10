from pydoc import locate
from typing import List

from sqlalchemy.ext.associationproxy import _AssociationList

from DataBase2 import Student, Group, Lesson, Visitation, Administration, Discipline, Professor, NotificationParam, \
    StudentsGroups, LessonsGroups


def select_by_id(session, mapper, ID):
    assert isinstance(ID, int), f'ID is not a number'
    assert mapper is not None
    if isinstance(mapper, str):
        return select_by_id(session, locate(f'DataBase2.{mapper}'), ID)
    else:
        return session.query(mapper).filter(mapper.id == ID).first()


def select(session, mapper, mapping):
    if mapper == Visitation:
        return session \
            .query(Visitation) \
            .filter(Visitation.lesson_id == mapping['lesson_id'],
                    Visitation.student_id == mapping['student_id']) \
            .first()
    elif mapper in [Administration, NotificationParam]:
        return session \
            .query(mapper) \
            .filter(mapper.id == mapping['id']) \
            .first()
    elif isinstance(mapper, str):
        return select(session, locate(f'DataBase2.{mapper}'), mapping)
    else:
        raise NotImplementedError(mapper)


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


def lessons_of(professor, groups=None, discipline=None, semester=None):
    total = set(Lesson.of(professor))

    if discipline is not None:
        total &= set(Lesson.of(discipline))
    if groups is not None:
        total &= set(Lesson.of(groups, intersect=True))
    if semester is not None:
        total = list(filter(lambda x: x.semester == semester, total))

    return sorted(total, key=lambda x: x.date)


def get_db_object(base, object_, session):
    """

    :param base:
    :param object_:
    :param session:
    :return: возвращает такой же объект в БД
    """
    if isinstance(object_, Visitation):
        old = session \
            .query(Visitation) \
            .filter(Visitation.lesson_id == object_.lesson_id, Visitation.student_id == object_.student_id).first()

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
