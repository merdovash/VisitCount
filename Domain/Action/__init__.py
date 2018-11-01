from DataBase2 import Visitation, Student, Lesson, Auth, Session
from Domain.Action.Exceptions import InvalidLogin, InvalidPassword
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

    print(f'new visitation: {visit}')
    return visit


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

    Synch(login, password, host, data, **kwargs)
