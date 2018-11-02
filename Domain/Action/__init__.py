from sqlalchemy import inspect

from DataBase2 import Visitation, Student, Lesson, Auth, Session, Professor, UpdateType, Administration, \
    NotificationParam
from Domain.Action.Exceptions import InvalidLogin, InvalidPassword
from Domain.Action.Update import create_update, create_delete_update
from Modules.FirstLoad.ClientSide import FirstLoad
from Modules.Synch.ClientSide import Synch


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

    create_update(visit, professor_id, update_type=UpdateType.NEW)

    return visit


def remove_visitation(visitation, professor_id):
    assert isinstance(visitation, Visitation), f'object {visitation} is not Visitation'
    assert isinstance(professor_id, int), f'object {professor_id} is not id (int)'

    professors = Professor.of(visitation)

    session = inspect(visitation).session

    session.delete(visitation)

    session.commit()

    assert isinstance(visitation, Visitation), f'object {visitation} is not Visitation'
    create_delete_update(visitation.id, type(visitation).__name__, professor_id, professors)



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


def first_load(login, password, host, **kwargs) -> None:
    assert isinstance(login, str), f'object {login} is not str'
    assert isinstance(password, str), f'object {password} is not str'

    FirstLoad(host, login, password, **kwargs).start()


def send_updates(login, password, host, data, **kwargs) -> None:
    assert isinstance(login, str), f'object {login} is not str'
    assert isinstance(password, str), f'object {password} is not str'
    assert isinstance(host, str), f'object {host} is not str'
    assert isinstance(data, dict), f'object {data} is not dict'

    Synch(login, password, host, data, **kwargs).start()


def start_lesson(lesson, professor) -> None:
    assert isinstance(lesson, Lesson), f'object {lesson} is not Lesson'
    assert isinstance(professor, Professor), f'object {professor} is not Professor'

    lesson.completed = True

    create_update(lesson, professor.id, UpdateType.UPDATE)


def create_administration(performer_id, **kwargs) -> Administration:
    assert isinstance(performer_id, int), f'object {performer_id} is not id (int)'

    session = Session()

    admin = Administration(**kwargs)

    session.add(admin)

    session.commit()

    np = NotificationParam(admin_id=admin.id, professor_id=performer_id, active=True)

    session.add(np)

    session.commit()

    create_update(admin, performer_id, UpdateType.NEW)
    create_update(np, performer_id, UpdateType.NEW)

    return admin
