from sqlalchemy import inspect

from DataBase2 import Visitation, Student, Lesson, Auth, Session, Professor, Administration, \
    NotificationParam, Parent, UpdateType
from Domain.Action import Updates
from Domain.Action.Exceptions import InvalidLogin, InvalidPassword
from Domain.Exception import UnnecessaryActionException
from Domain.functools.Dict import to_dict


def changes_ids(items, new_ids, session=None):
    assert len(items) == len(new_ids), f'{len(items)}!={len(new_ids)}'

    for item in items:
        session.merge(item)
        item.id = -item.id

    session.commit()

    for i, item in enumerate(items):
        item.id = new_ids[i]

    session.commit()


def new_visitation(student, lesson, professor_id, session=None) -> Visitation:
    assert isinstance(student, Student), f'object {student} is not Student'
    assert isinstance(lesson, Lesson), f'object {lesson} is not Lesson'
    assert isinstance(professor_id, int), f'object {professor_id} is not id (int)'

    if session is None:
        session = Session()

    old_visit = session \
        .query(Visitation) \
        .filter(Visitation.lesson_id == lesson.id) \
        .filter(Visitation.student_id == student.id) \
        .first()
    if old_visit is not None:
        raise UnnecessaryActionException

    visit = Visitation(student_id=student.id, lesson_id=lesson.id)

    session.add(visit)

    session.commit()

    try:
        visit.id
    except:
        try:
            session.merge(visit)
        except:
            raise

    Updates.New.row(
        table=Visitation,
        new_row_id=visit.id,
        performer_id=professor_id,
        update_type=UpdateType.visit_new
    )

    return visit


def remove_visitation(visitation, professor_id):
    assert isinstance(visitation, Visitation), f'object {visitation} is not Visitation'
    assert isinstance(professor_id, int), f'object {professor_id} is not id (int)'

    professors = Professor.of(visitation)

    session = inspect(visitation).session

    session.delete(visitation)

    session.commit()

    print('visitation after delete', visitation)

    assert isinstance(visitation, Visitation), f'object {visitation} is not Visitation'
    Updates.Delete.row(
        deleted_object=to_dict(visitation),
        deleted_object_table=type(visitation).__name__,
        performer_id=professor_id,
        professors_affected=professors,
        update_type=UpdateType.visit_del
    )


def log_in(login, password, session=None) -> Auth:
    assert isinstance(login, str), f'object {login} is not str'
    assert isinstance(password, str), f'object {password} is not str'

    if session is None:
        session = Session()

    query = session.query(Auth).filter_by(login=login)

    if query.first() is None:
        raise InvalidLogin()
    else:
        auth = query.filter_by(password=password).first()
        if auth is None:
            raise InvalidPassword()
        else:
            return auth


def start_lesson(lesson, professor) -> None:
    assert isinstance(lesson, Lesson), f'object {lesson} is not Lesson'
    assert isinstance(professor, Professor), f'object {professor} is not Professor'

    if lesson.completed:
        raise UnnecessaryActionException(f'{lesson} is already started')

    lesson.completed = True

    Updates.Changed.row(
        changed_row_id=lesson.id,
        table_name=type(lesson).__name__,
        performer_id=professor.id,
        update_type=UpdateType.lesson_completed
    )


def create_administration(performer_id, **kwargs) -> Administration:
    assert isinstance(performer_id, int), f'object {performer_id} is not id (int)'

    session = Session()

    admin = Administration(**kwargs)

    session.add(admin)

    session.commit()

    np = NotificationParam(
        admin_id=admin.id,
        professor_id=performer_id,
        active=True)

    session.add(np)

    session.commit()

    Updates.New.row(
        table=Administration,
        new_row_id=admin.id,
        performer_id=performer_id,
        update_type=UpdateType.contact_admin_new)
    Updates.New.row(
        table=NotificationParam,
        new_row_id=np.id,
        performer_id=performer_id,
    )

    return admin


def delete_contact(contact, professor_id):
    assert isinstance(contact, (Administration, Parent)), f'object {contact} is not Administration or Parent'
    assert isinstance(professor_id, int), f'object {professor_id} is not id (int)'

    session = inspect(contact).session

    affected_professors = Professor.of(contact)

    if isinstance(contact, Administration):
        nps = NotificationParam.of(contact)

        for np in nps:
            Updates.Delete.row(
                deleted_object=to_dict(np),
                deleted_object_table=type(np).__name__,
                performer_id=professor_id,
                update_type=UpdateType.contact_admin_del
            )

    session.delete(contact)

    session.commit()


def change_student_card_id(student, new_card_id, professor_id):
    assert isinstance(student, Student)
    assert isinstance(new_card_id, (str, int)), f'card_id {new_card_id} is not id'

    if student.card_id == new_card_id:
        raise UnnecessaryActionException(f'Student already has same card_id {student.card_id}=={new_card_id}')

    session = inspect(student).session

    student.card_id = new_card_id

    session.commit()

    Updates.Changed.row(
        changed_row_id=student.id,
        table_name=type(student).__name__,
        performer_id=professor_id,
        update_type=UpdateType.student_card_id_updated
    )
