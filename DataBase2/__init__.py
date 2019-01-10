"""

safsdf
"""
import os
import sys
from datetime import datetime
from threading import Lock
from typing import List, Union, Dict, Any, Type

from sqlalchemy import create_engine, UniqueConstraint, Column, Integer, String, ForeignKey, Boolean, DateTime
from sqlalchemy.ext.associationproxy import association_proxy, _AssociationList
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship, scoped_session, backref
from sqlalchemy.pool import SingletonThreadPool, StaticPool, NullPool
from sqlalchemy.sql import ClauseElement

from DataBase2.config2 import Config
from Domain.ArgPars import get_argv
from Domain.Date import study_week, study_semester
from Domain.Exception.Authentication import InvalidPasswordException, InvalidLoginException, InvalidUidException
from Domain.Validation.Values import Get
from Domain.functools.List import DBList
from Parser import IJSON
from Parser.JsonParser import JsonParser

try:
    root = sys.modules['__main__'].__file__
    print(sys.modules['__main__'].__file__)
except AttributeError:
    root = "run_client.py"

print(os.path.basename(root))
root = os.path.basename(root)

datetime_format = "%Y-%m-%d %H:%M:%S"


def create_threaded():
    db_path = 'sqlite:///{}'.format(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'db.db'))

    engine = create_engine(db_path, echo=False, poolclass=SingletonThreadPool)

    Base = declarative_base(bind=engine)

    try:
        fh = open(db_path.split('///')[1], 'r')
        fh.close()
    except FileNotFoundError:
        fh = open(db_path.split('///')[1], 'w+')
        fh.close()
        _new = True

    Session = scoped_session(sessionmaker(bind=engine, autoflush=False))
    # session = Session()

    metadata = Base.metadata

    return Session, Base, metadata, engine


def create():
    _new = False
    if root == 'run_server.py':
        engine = create_engine(Config.connection_string,
                               pool_pre_ping=True,
                               poolclass=NullPool,
                               pool_recycle=3600)

    else:
        db_path = 'sqlite:///{}'.format(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'db2.db'))

        engine = create_engine(db_path,
                               echo=True if get_argv('--db-echo') else False,
                               poolclass=StaticPool,
                               connect_args={'check_same_thread': False})

        try:
            fh = open(db_path.split('///')[1], 'r')
            fh.close()
        except FileNotFoundError:
            fh = open(db_path.split('///')[1], 'w+')
            fh.close()
            _new = True

    Base = declarative_base(bind=engine)

    Session = scoped_session(sessionmaker(bind=engine, autoflush=False, expire_on_commit=False))

    metadata = Base.metadata

    return Session, Base, metadata, engine, _new


Session, Base, metadata, engine, _new = create()

lock = Lock()


def session_user(func):
    def f(*args, **kwargs):
        lock.acquire()
        try:
            res = func(*args, **kwargs)
        except:
            raise
        finally:
            lock.release()
        return res

    return f


def UserSession(user, session=None):
    if session is None:
        s = Session()
    else:
        s = session

    if isinstance(user, _DBPerson):
        setattr(s, 'user', user)

    return s


class _DBObject(IJSON):
    __table_args__ = {
        'mysql_engine': 'InnoDB',
        'mysql_charset': 'utf8',
        'mysql_collate': 'utf8_general_ci'
    }

    id = Column(Integer, primary_key=True, unique=True, autoincrement=True)

    def __init__(self, **kwargs):
        Base.__init__(self, id=kwargs.pop('id', None), **kwargs)

    def __repr__(self):
        return "<{type}({fields})>".format(
            type=type(self).__name__,
            fields=', '.join("{name}={value}".format(name=name, value=value)
                             for name, value in self._dict().items())
        )

    def __hash__(self):
        return hash(f'{type(self).__name__}:{self.id}')

    @classmethod
    def column_type(cls, name):
        python_type = cls.table().c[name].type.python_type
        if python_type == datetime:
            return Get.datetime
        if python_type == bool:
            return Get.bool
        return python_type

    def _dict(self) -> dict:
        return {
            name: getattr(self, name)
            for name in self.table().c.keys()
        }

    def dict(self):
        return {key: item for key, item in self._dict() if key[0] != '_'}

    def to_json(self) -> str:
        r = self._dict()
        return JsonParser.dump(r)

    @classmethod
    def of(cls, obj, with_deleted=False):
        raise NotImplementedError(cls)

    @classmethod
    def new(cls, session=None, **kwargs):
        obj = cls(**kwargs)
        if session is not None:
            session.add(obj)
        return obj

    @classmethod
    def table(cls):
        return cls.__table__

    @classmethod
    def insert_or_ignore(cls, data: List[Dict[str, Any]]):
        cls.table().insert(
            prefixes=['OR IGNORE']
        ).execute(data)

    @classmethod
    def get(cls, session, **kwargs) -> '_DBObject':
        return session.query(cls).filter_by(**kwargs).first()

    @classmethod
    def get_or_create(cls, session, **kwargs):
        instance = cls.get(session, **kwargs)
        if instance:
            return instance
        else:
            params = dict((k, v) for k, v in kwargs.items() if not isinstance(v, ClauseElement))
            instance = cls(**params)
            session.add(instance)
            return instance

    @staticmethod
    def class_(name) -> Type['_DBObject']:
        return eval(name)

    def __getitem__(self, item):
        return self._dict()[item]

    def __eq__(self, other):
        if isinstance(other, _DBObject):
            return super().__eq__(other)

        if isinstance(other, dict):
            return self._dict() == other

        super().__eq__(other)


class _DBTrackedObject(_DBObject):
    _created = Column(DateTime, default=datetime.now)
    _updated = Column(DateTime, default=datetime.now, onupdate=datetime.now)
    _is_deleted = Column(Boolean, default=False)
    _deleted = Column(DateTime)

    def delete(self):
        self._is_deleted = True
        self._deleted = datetime.now()

    def restore(self):
        self._deleted = None
        self._is_deleted = False

    def is_deleted(self):
        return self._is_deleted


class _DBPerson(_DBTrackedObject):
    last_name = Column(String(50), nullable=False)
    first_name = Column(String(50), nullable=False)
    middle_name = Column(String(50), default="")
    sex = Column(Boolean, default=True)
    email = Column(String(200))

    def __init__(self, **kwargs):
        super().__init__(
            last_name=kwargs.pop('last_name', ''),
            first_name=kwargs.pop('first_name', ''),
            middle_name=kwargs.pop('middle_name', ''),
            sex=kwargs.pop('sex', True),
            email=kwargs.pop('email', ''),
            **kwargs)

    session = None

    @classmethod
    def get_by_id(cls, id):
        """
        Возвращает Person по id
        Работает для всех наследников класса и возвращает объект наследника
        :param id:
        :return:
        """
        user_session = Session()

        user = user_session.query(cls).filter(cls.id == id).first()

        if user is not None:
            return UserSession(user, user_session)
        else:
            raise ValueError('user of {id} not found'.format(id=id))


class StudentsGroups(Base, _DBTrackedObject):
    """
    Ассоциативная таблица Студентов - Групп
    """
    __tablename__ = 'students_groups'
    __table_args__ = (
        UniqueConstraint('student_id', 'group_id', name='students_groups_UK'),
        _DBObject.__table_args__
    )
    student_id = Column(Integer, ForeignKey('students.id'))
    group_id = Column(Integer, ForeignKey('groups.id'))

    @classmethod
    def of(cls, obj, with_deleted=False):
        if isinstance(obj, Professor):
            return DBList(
                obj.session \
                    .query(StudentsGroups)
                    .distinct(StudentsGroups.id) \
                    .join(Group) \
                    .join(LessonsGroups) \
                    .join(Lesson) \
                    .join(Professor) \
                    .filter(Professor.id == obj.id) \
                    .all(),
                with_deleted=with_deleted)
        raise NotImplementedError(type(obj), obj)


class LessonsGroups(Base, _DBTrackedObject):
    """
    Ассоциативная таблица Занятий - Групп
    """
    __tablename__ = 'lessons_groups'
    __table_args__ = (
        UniqueConstraint('lesson_id', 'group_id', name='lesson_groups_UK'),
        _DBObject.__table_args__
    )

    lesson_id = Column(Integer, ForeignKey('lessons.id'))
    group_id = Column(Integer, ForeignKey('groups.id'))

    @classmethod
    def of(cls, obj, with_deleted=False):
        if isinstance(obj, Professor):
            return DBList(
                obj.session
                    .query(LessonsGroups)
                    .distinct(LessonsGroups.id)
                    .join(Lesson)
                    .join(Professor)
                    .filter(Professor.id == obj.id).
                    all(),
                with_deleted=with_deleted)
        raise NotImplementedError(type(obj))


class StudentsParents(Base, _DBTrackedObject):
    """
    Ассоциативная таблица Студентов - Родителей
    """
    __tablename__ = 'students_parents'
    __table_args__ = (
        UniqueConstraint('parent_id', 'student_id', name='student_parent_UK'),
        _DBObject.__table_args__
    )

    parent_id = Column(Integer, ForeignKey('parents.id'))
    student_id = Column(Integer, ForeignKey('students.id'))

    @classmethod
    @DBList.wrapper
    def of(cls, obj, with_deleted=False):
        if isinstance(obj, Professor):
            return obj.session \
                .query(StudentsParents) \
                .distinct(StudentsParents.id) \
                .join(Student) \
                .join(StudentsGroups) \
                .join(Group) \
                .join(LessonsGroups) \
                .join(Lesson) \
                .join(Professor) \
                .filter(Professor.id == obj.id) \
                .all()
        raise NotImplementedError(obj)


class Visitation(Base, _DBTrackedObject):
    """
    Таблица посещений занятий
    """

    __tablename__ = 'visitations'
    __table_args__ = (
        UniqueConstraint('student_id', 'lesson_id', name='visitation_UK'),
        _DBObject.__table_args__
    )

    student_id = Column(Integer, ForeignKey('students.id'))
    lesson_id = Column(Integer, ForeignKey('lessons.id'))

    def __repr__(self):
        return f'<Visitation(id={self.id}, student_id={self.student_id},' \
            f' lesson_id={self.lesson_id})>'

    @classmethod
    def of(cls, obj, with_deleted=False) -> List['Visitation']:
        """

        :param obj: объект или список объектов базы данных
        :param with_deleted: включать ли удаленные объекты в список
        :return: список посещений объекта
        """
        if isinstance(obj, (list, _AssociationList)):
            return DBList([Visitation.of(o) for o in obj], flat=True, unique=True, with_deleted=with_deleted)

        if isinstance(obj, (Student, Lesson)):
            return DBList(obj.visitations, with_deleted=with_deleted)

        if isinstance(obj, Group):
            return DBList(Visitation.of(obj.students), flat=True, with_deleted=with_deleted)

        if isinstance(obj, (Professor, Discipline)):
            return DBList([o.visitations for o in obj.lessons], flat=True, with_deleted=with_deleted)

        raise NotImplementedError(type(obj))

    @classmethod
    def get(cls, session, student_id=None, lesson_id=None, **kwargs):
        if student_id is None or lesson_id is None:
            if lesson_id is not None:
                kwargs['lesson_id'] = lesson_id
            if student_id is not None:
                kwargs['student_id'] = student_id
            return super().get(session, **kwargs)
        return session \
            .query(Visitation) \
            .filter(Visitation.student_id == student_id) \
            .filter(Visitation.lesson_id == lesson_id) \
            .first()


class UserType(int):
    STUDENT = 0
    PROFESSOR = 1
    PARENT = 2
    ADMIN = 3


class Auth(Base, _DBObject):
    """
    Таблица пользователей
    """
    __tablename__ = 'auth5'

    login = Column(String(40), unique=True)
    password = Column(String(40))
    uid = Column(String(40), unique=True)
    user_type = Column(Integer)
    user_id = Column(Integer)

    __user = None
    session: Session = None

    @property
    def user(self) -> Union['Student', 'Professor']:
        """

        :return: Professor or Student
        """
        if self.__user is None:
            if self.user_type == UserType.STUDENT:
                self.__user: Student = self.session \
                    .query(Student) \
                    .filter(Student.id == self.user_id) \
                    .first()
            elif self.user_type == UserType.PROFESSOR:
                self.__user: Professor = self.session \
                    .query(Professor) \
                    .filter(Professor.id == self.user_id) \
                    .first()
                self.__user.session = self.session
                self.__user.auth = self

        return self.__user

    @staticmethod
    def log_in(login=None, password=None) -> 'Auth':
        """

        Производит аутентифкацию в двухфакторном режиме

        :param login: логин (открытый ключ)
        :param password: пароль (секретный ключ)
        :return: учетную запись пользователя
        """
        sess = Session()

        q = sess.query(Auth).filter(Auth.login == login)
        if q.first():
            auth = q.filter(Auth.password == password).first()
            if auth:
                auth.session = sess
                auth.session = UserSession(auth.user, sess)
                return auth
            else:
                raise InvalidPasswordException()
        else:
            raise InvalidLoginException()

    @staticmethod
    def log_in_by_uid(uid):
        sess = Session()

        auth = sess.query(Auth).filter(Auth.uid == uid).first()
        if auth:
            return auth
        else:
            raise InvalidUidException()

    def __repr__(self):
        return f"<Auth(id={self.id}," \
            f" user_type={self.user_type}," \
            f" user_id={self.user_id})>"


class Discipline(Base, _DBTrackedObject):
    """
    Таблица дисциплин
    """
    __tablename__ = 'disciplines'

    name = Column(String(40), nullable=False)
    full_name = Column(String(200))

    lessons = relationship('Lesson', backref=backref('discipline'))

    def __repr__(self):
        return f"<Discipline(id={self.id}," \
            f" name={self.name})>"

    @classmethod
    def of(cls, obj, with_deleted=False) -> List['Discipline']:
        """

        :param obj: объект или список объектов базы данных
        :param with_deleted: включать ли удаленные объекты в список
        :return: список дисциплин объекта
        """
        if isinstance(obj, (list, _AssociationList)):
            return DBList([Discipline.of(o) for o in obj], flat=True, unique=True)
        elif isinstance(obj, Lesson):
            return DBList([obj.discipline], with_deleted=with_deleted)
        elif isinstance(obj, Professor):
            return DBList([lesson.discipline for lesson in obj.lessons], flat=True, unique=True,
                          with_deleted=with_deleted)
        else:
            raise NotImplementedError(type(obj))


class Lesson(Base, _DBTrackedObject):
    """
    Lesson
    """
    __tablename__ = 'lessons'
    __table_args__ = (
        UniqueConstraint('professor_id', 'date', name='lesson_UK'),
        _DBObject.__table_args__
    )

    professor_id = Column(Integer, ForeignKey('professors.id'), nullable=False)
    discipline_id = Column(Integer, ForeignKey('disciplines.id'), nullable=False)
    type = Column(Integer, nullable=False)
    date = Column(DateTime, nullable=False)
    completed = Column(Boolean, nullable=False)
    room_id = Column(String(40), nullable=False)

    _groups = relationship('LessonsGroups', backref=backref('lesson'))
    groups = association_proxy('_groups', 'group')

    visitations = relationship('Visitation', backref=backref('lesson'))

    def __repr__(self):
        return f"<Lesson(id={self.id}, professor_id={self.professor_id}," \
            f" discipline_id={self.discipline_id}, " \
            f"date={self.date}, type={self.type}," \
            f" completed={self.completed})>"

    _week = None

    @property
    def week(self):
        if self._week is None:
            self._week = study_week(self.date)
        return self._week

    _semester = None

    @property
    def semester(self):
        """

        :return: номер семестра этого занятия
        """
        if self._semester is None:
            self._semester = study_semester(self.date)
        return self._semester

    @classmethod
    def of(cls, obj, intersect=False, with_deleted=False) -> List['Lesson']:
        """

        :param semester:
        :param intersect:
        :param obj: объект или спсиок объектов базы данных
        :param with_deleted: включать ли в список удаленные объекты
        :return: список родителей, отоносящихся к объекту
        """
        if isinstance(obj, (list, _AssociationList)):
            if intersect:
                lessons = None
                for o in obj:
                    lessons = Lesson.of(o) \
                        if lessons is None \
                        else list(set(lessons).intersection(Lesson.of(o)))
                return DBList(lessons,
                              with_deleted=with_deleted,
                              flat=True)

            else:
                return DBList([Lesson.of(o) for o in obj],
                              flat=True,
                              unique=True,
                              with_deleted=with_deleted)

        elif isinstance(obj, (Professor, Discipline, Group)):
            return DBList(obj.lessons,
                          with_deleted=with_deleted)

        elif isinstance(obj, Student):
            return DBList([Lesson.of(o) for o in obj.groups],
                          flat=True,
                          with_deleted=with_deleted)

        else:
            raise NotImplementedError(type(obj))


class Administration(Base, _DBPerson):
    """
    Таблица администраций
    """
    __tablename__ = 'administrations'

    notification = relationship('NotificationParam', backref=backref("admin", cascade="all,delete"),
                                passive_updates=False)
    professors = association_proxy('notification', 'professor')

    def __repr__(self):
        return f"<Administration(id={self.id}, card_id={self.email}, " \
            f"last_name={self.last_name}, first_name={self.first_name}, " \
            f"middle_name={self.middle_name})>"

    @classmethod
    def of(cls, obj, with_deleted=False) -> List['Administration']:
        """
        Возвращает список Администраторов, которые относятся к переданому объекту
        :param obj: Объект базы данных
        :param with_deleted: список включает удаленные объекты
        :return: список
        """
        if isinstance(obj, (list, _AssociationList)):
            return DBList([Administration.of(o) for o in obj], flat=True, unique=True, with_deleted=with_deleted)
        elif isinstance(obj, Professor):
            return DBList(obj.admins, with_deleted=with_deleted)
        elif isinstance(obj, NotificationParam):
            return DBList(obj.admin, with_deleted=with_deleted)
        else:
            raise NotImplementedError(type(obj))

    @staticmethod
    def active_of(obj):
        """

        :param obj: объект или спсиок объектов базы данных
        :return: спсиок активных оповещений
        """
        if isinstance(obj, Professor):
            nps = list(filter(lambda np: np.active, NotificationParam.of(obj)))
            return Administration.of(nps)
        else:
            raise NotImplementedError(type(obj))


class Professor(_DBPerson, Base):
    """
    Таблица преподавателей
    """
    __tablename__ = 'professors'

    card_id = Column('card_id', String(40), unique=True)

    _last_update_in = Column(DateTime, default=datetime.now)
    _last_update_out = Column(DateTime)

    lessons: List[Lesson] = relationship("Lesson", backref=backref('professor'), order_by="Lesson.date")

    _admins = relationship('NotificationParam', backref="professor")
    admins = association_proxy('_admins', 'admin')

    session: Session = None
    auth: Auth = None

    @classmethod
    def of(cls, obj, with_deleted=False) -> List['Professor']:
        """

        :param obj: объект или спсиок объектов базы данных
        :param with_deleted: включать ли в список удаленные объекты
        :return: список преподавателей, отоносящихся к объекту
        """
        if isinstance(obj, (list, _AssociationList, set)):
            return DBList([Professor.of(o) for o in obj],
                          flat=True,
                          unique=True,
                          with_deleted=with_deleted)

        elif isinstance(obj, (Lesson, NotificationParam)):
            return DBList([obj.professor])

        elif isinstance(obj, Visitation):
            return Professor.of(obj.lesson, with_deleted=with_deleted)

        elif isinstance(obj, Administration):
            return DBList(obj.professors, with_deleted=with_deleted)

        elif isinstance(obj, Student):
            return Professor.of(obj.groups, with_deleted=with_deleted)

        elif isinstance(obj, Group):
            return Professor.of(obj.lessons, with_deleted=with_deleted)

        else:
            raise NotImplementedError(type(obj))

    def updates(self, last_in: datetime = None) -> Dict[str, Dict[str, List]]:
        """

        :return: кортеж из трех словарей:
            созданные объекты этим преподавтелем с момента последней отправки,
            измененные объекты этим преподавтелем с момента последней отправки,
            удаленные объекты этим преподавтелем с момента последней отправки
        """

        if last_in is None:
            created_cond = lambda item: item._created and item._created >= self._last_update_out
            updated_cond = lambda item: item._updated and item._updated >= self._last_update_out
            deleted_cond = lambda item: item._deleted and item._is_deleted and item._deleted >= self._last_update_out
        else:
            created_cond = lambda item: item._created and item._created >= last_in
            updated_cond = lambda item: item._updated and item._updated >= last_in
            deleted_cond = lambda item: item._deleted and item._is_deleted and item._deleted >= last_in

        created = {}
        updated = {}
        deleted = {}

        if self._last_update_out is None:
            self._last_update_out = datetime(2008, 1, 1)

        for class_ in [class_ for class_ in _DBTrackedObject.__subclasses__() if class_.__name__[0] != '_']:
            data: List[_DBTrackedObject] = DBList(class_.of(self, with_deleted=True), flat=True, unique=True)

            created[class_.__name__] = [data.pop(i) for i in range(len(data) - 1, -1, -1) if created_cond(data[i])]
            updated[class_.__name__] = [data.pop(i) for i in range(len(data) - 1, -1, -1) if updated_cond(data[i])]
            deleted[class_.__name__] = [data.pop(i) for i in range(len(data) - 1, -1, -1) if deleted_cond(data[i])]

        return dict(created=created, updated=updated, deleted=deleted)


class NotificationParam(Base, _DBTrackedObject):
    """
    Таблица парметров оповещений
    """

    __tablename__ = 'notifications'
    __table_args__ = (
        UniqueConstraint('professor_id', 'admin_id', name='notification_param_UK'),
        _DBObject.__table_args__
    )

    professor_id = Column(Integer, ForeignKey('professors.id'))
    admin_id = Column(Integer, ForeignKey('administrations.id'))
    active = Column(Boolean)

    @classmethod
    def of(cls, obj, with_deleted=False) -> List['NotificationParam']:
        """

        :param obj: Объект базы данных или список объектов
        :param with_deleted: включать ли в список удаленные объекты
        :return: список Парааметров оповещений, которые отностятся к переданному объекту
        """
        if isinstance(obj, (list, _AssociationList)):
            return DBList([NotificationParam.of(o, with_deleted=with_deleted) for o in obj],
                          flat=True,
                          unique=True,
                          with_deleted=with_deleted)

        elif isinstance(obj, Professor):
            return DBList(obj._admins,
                          with_deleted=with_deleted)

        elif isinstance(obj, Administration):
            return DBList(obj.notification,
                          with_deleted=with_deleted)
        else:
            raise NotImplementedError(type(obj))

    def __repr__(self):
        return f"<NotificationParam (id={self.id}, professor_id={self.professor_id}, admin_id={self.admin_id}, " \
            f"active={self.active})>"


class Group(Base, _DBTrackedObject):
    """
    Таблица групп
    """
    __tablename__ = 'groups'

    name = Column(String(40))

    _students = relationship('StudentsGroups', backref=backref('group'))
    students = association_proxy('_students', 'student')

    _lessons = relationship('LessonsGroups', backref=backref('group'))
    lessons = association_proxy('_lessons', 'lesson')

    def __repr__(self):
        return f"<Group(id={self.id}, name={self.name})>"

    @classmethod
    def of(cls, obj, with_deleted=False, flat_list=False) -> List['Group'] or DBList:
        """

        :param flat_list: исключить из результата наборы групп (оставить только перечень групп)
        :param obj: объект или спсиок объектов базы данных
        :param with_deleted: включать ли в список удаленные объекты
        :return: список групп, отоносящихся к объекту
        """
        if isinstance(obj, (list, _AssociationList)):
            return DBList([Group.of(o) for o in obj], unique=True, with_deleted=with_deleted, flat=flat_list)
        elif isinstance(obj, Lesson):
            return DBList(obj.groups, flat=flat_list)
        elif isinstance(obj, Professor):
            return DBList([frozenset(lesson.groups) if len(lesson.groups) > 1 else DBList(lesson.groups)
                           for lesson in obj.lessons],
                          flat=flat_list,
                          unique=True,
                          with_deleted=with_deleted)

        elif isinstance(obj, Discipline):
            return DBList([Group.of(lesson) for lesson in obj.lessons],
                          unique=True,
                          with_deleted=with_deleted)
        elif isinstance(obj, Student):
            return DBList(obj.groups, with_deleted=with_deleted)
        else:
            raise NotImplementedError(type(obj))


class Student(Base, _DBPerson):
    """
    Таблица студентов
    """

    __tablename__ = 'students'

    card_id = Column(String(40))

    _parents = relationship('StudentsParents', backref=backref('student'))
    parents = association_proxy('_parents', 'parent')

    _groups = relationship('StudentsGroups', backref=backref('student'))
    groups = association_proxy('_groups', 'group')

    visitations = relationship("Visitation", backref=backref('student'))

    def __repr__(self):
        return f"<Student(id={self.id}, card_id={self.card_id}," \
            f" last_name={self.last_name}, first_name={self.first_name}, " \
            f"middle_name={self.middle_name})>"

    @classmethod
    def of(cls, obj, with_deleted=False) -> List['Student']:
        """

        :param obj: объект или спсиок объектов базы данных
        :param with_deleted: включать ли в список удаленные объекты
        :return: список студентов, отоносящихся к объекту
        """
        if isinstance(obj, (list, _AssociationList)):
            return DBList([Student.of(o) for o in obj],
                          flat=True,
                          unique=True,
                          with_deleted=with_deleted)

        elif isinstance(obj, Group):
            return DBList(sorted(obj.students, key=lambda student: student.last_name),
                          with_deleted=with_deleted,
                          unique=True)

        elif isinstance(obj, Lesson):
            return DBList([Student.of(group) for group in obj.groups],
                          flat=True,
                          unique=True,
                          with_deleted=with_deleted)

        elif isinstance(obj, (Professor, Discipline)):
            return DBList(map(lambda lesson: Student.of(lesson.groups), obj.lessons),
                          flat=True,
                          unique=True,
                          with_deleted=with_deleted)
        else:
            raise NotImplementedError(type(obj))


class Parent(Base, _DBPerson):
    """
    Таблица содержащая информациюо родителях
    """
    __tablename__ = "parents"

    _students = relationship("StudentsParents", backref=backref('parent'))
    students = association_proxy('_students', 'student')

    @classmethod
    def of(cls, obj, with_deleted=False) -> List['Parent']:
        """

        :param obj: объект или спсиок объектов базы данных
        :param with_deleted: включать ли в список удаленные объекты
        :return: список родителей, отоносящихся к объекту
        """
        if isinstance(obj, (list, _AssociationList)):
            return DBList([Parent.of(o) for o in obj],
                          flat=True,
                          unique=True)

        elif isinstance(obj, Student):
            return DBList(obj.parents)

        elif isinstance(obj, Professor):
            return DBList(Parent.of(Student.of(obj)),
                          flat=True,
                          unique=True,
                          with_deleted=with_deleted)

        else:
            raise NotImplementedError(type(obj))


if _new:
    Base.metadata.create_all(engine)

# events

# for class_ in _DBTrackedObject.__subclasses__():
#     if Base in class_.__bases__:
#         for atr in dir(class_):
#             if atr != 'id' and atr[0] != '_':
#                 if isinstance(getattr(class_, atr), InstrumentedAttribute):
#                     print(eval(f"{class_.__name__}.{atr}"))
#
#
#                     @event.listens_for(eval(f"{class_.__name__}.{atr}"), 'set')
#                     def receive_set(target, value, oldvalue, initiator):
#                         print('fdsgdghfh')
#                         target._updated = datetime.now()

if __name__ == '__main__':
    d = Visitation.get(Session(), id=3161)

    print(d._is_deleted)
