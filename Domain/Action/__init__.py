from sqlalchemy import inspect

from DataBase2 import Visitation, Student, Lesson, Auth, Session, Professor, Administration, \
    NotificationParam, Parent
from Domain.Action import Updates
from Domain.Action.Exceptions import InvalidLogin, InvalidPassword


def new_visitation(student, lesson, professor_id, session=None) -> Visitation:
    assert isinstance(student, Student), f'object {student} is not Student'
    assert isinstance(lesson, Lesson), f'object {lesson} is not Lesson'
    assert isinstance(professor_id, int), f'object {professor_id} is not id (int)'

    if session is None:
        session = Session()

    visit = Visitation(student_id=student.id, lesson_id=lesson.id)

    session.add(visit)

    session.commit()

    try:
        print(f'new visitation: {visit}')
    except:
        try:
            session.merge(visit)
        except:
            raise

    Updates.New.row(visit, professor_id)

    return visit


def remove_visitation(visitation, professor_id):
    assert isinstance(visitation, Visitation), f'object {visitation} is not Visitation'
    assert isinstance(professor_id, int), f'object {professor_id} is not id (int)'

    professors = Professor.of(visitation)

    session = inspect(visitation).session

    session.delete(visitation)

    session.commit()

    assert isinstance(visitation, Visitation), f'object {visitation} is not Visitation'
    Updates.Delete.row(visitation.id, type(visitation).__name__, professor_id, professors)


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

    lesson.completed = True

    Updates.Changed.row(lesson.id, type(lesson).__name__, professor.id)


def create_administration(performer_id, **kwargs) -> Administration:
    assert isinstance(performer_id, int), f'object {performer_id} is not id (int)'

    session = Session()

    admin = Administration(**kwargs)

    session.add(admin)

    session.commit()

    np = NotificationParam(admin_id=admin.id, professor_id=performer_id, active=True)

    session.add(np)

    session.commit()

    Updates.New.row(admin, performer_id)
    Updates.New.row(np, performer_id)

    return admin


def delete_contact(contact, professor_id):
    assert isinstance(contact, (Administration, Parent)), f'object {contact} is not Administration or Parent'
    assert isinstance(professor_id, int), f'object {professor_id} is not id (int)'

    session = inspect(contact).session

    if isinstance(contact, Administration):
        nps = NotificationParam.of(contact)

        for np in nps:
            Updates.Delete.row(np.id, type(np).__name__, professor_id)

    session.delete(contact)

    session.commit()
