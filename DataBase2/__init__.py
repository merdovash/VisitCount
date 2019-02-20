"""

safsdf
"""
import os
import pathlib
import sys
from abc import ABC
from datetime import datetime
from typing import List, Union, Dict, Any, Type, Callable

from sqlalchemy import create_engine, UniqueConstraint, Column, Integer, String, ForeignKey, Boolean, DateTime, inspect
from sqlalchemy.ext.associationproxy import association_proxy, _AssociationList
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship, scoped_session, backref
from sqlalchemy.pool import SingletonThreadPool, StaticPool, NullPool
from sqlalchemy.sql import ClauseElement

from DataBase2.config2 import Config
from Domain.ArgPars import get_argv
from Domain.Date import study_week, study_semester
from Domain.Exception.Authentication import InvalidPasswordException, InvalidLoginException, InvalidUidException, \
    UnauthorizedError
from Domain.Validation.Values import Get
from Domain.functools.Decorator import listed, filter_deleted
from Domain.functools.List import DBList
from Parser import IJSON

try:
    root = sys.modules['__main__'].__file__
except AttributeError:
    root = "run_client.py"

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
    if root == 'run_server.py' and os.name != 'nt':
        engine = create_engine(Config.connection_string,
                               pool_pre_ping=True,
                               echo=True if get_argv('--db-echo') else False,
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
            pathlib.Path('DataBase2').mkdir(parents=True, exist_ok=True)
            fh = open(db_path.split('///')[1], 'w+')
            fh.close()
            _new = True

    Base = declarative_base(bind=engine)

    Session = scoped_session(sessionmaker(bind=engine, autoflush=False, expire_on_commit=False))

    metadata = Base.metadata

    return Session, Base, metadata, engine, _new


Session, Base, metadata, engine, _new = create()


class ISession:
    def commit(self):
        pass

    def query(self, table: Type['_DBObject']):
        pass

    def flush(self):
        pass

    def expire_all(self):
        pass

    def add(self, obj: '_DBObject'):
        pass

    def close(self):
        pass


Session: Callable[[], ISession] = Session


def is_None(x):
    return x in [None, 'None', 'null']


class _ListedValues(int, IJSON):
    __values__ = {}

    def __new__(cls, inst):
        if isinstance(inst, int):
            return inst
        elif isinstance(inst, str):
            for key, value in cls.__values__.items():
                if inst == value:
                    return key
        raise ValueError('unacceptable value')

    def to_json(self):
        return self

    def __str__(self):
        return self.__values__[self]

    @classmethod
    def types(cls):
        return cls.__values__

    @classmethod
    def derived(self, obj)->Type:
        if isinstance(obj, _DBObject) or issubclass(obj, _DBObject):
            if hasattr(obj, 'Type'):
                return obj.Type
        raise ValueError(f'No type inside class {obj}')


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
    def column_type(cls, name: str) -> callable or Type:
        """
        Возвращает функцию, которая воспроизводит класс объекта для атрибута name
        :param name: имя атрибута
        :return: callable
        """
        if name == 'type':
            return _ListedValues.derived(cls)
        python_type = cls.table().c[name].type.python_type
        if python_type == datetime:
            return Get.datetime
        if python_type == bool:
            return Get.bool
        if python_type == int:
            return Get.int
        return python_type

    @classmethod
    def column_str(cls, name):
        """
        Возвращает строкое представление значения атрибута name
        :param name: имя атрибута
        :return: str
        """
        python_type = cls.table().c[name].type.python_type
        if python_type == datetime:
            def datetime_to_str(x):
                if is_None(x):
                    return str(None)
                return x.strftime("%Y-%m-%d %H:%M:%S")

            return datetime_to_str
        if python_type == str:
            return lambda x: x
        return str

    def _dict(self) -> dict:
        return {
            name: getattr(self, name)
            for name in self.table().c.keys()
        }

    def dict(self):
        """
        Возвращает словарь {атрибут:значение}
        :return:
        """
        return {key: item for key, item in self._dict() if key[0] != '_'}

    def to_json(self) -> str:
        """
        Возвращает строковое представление json объекта, отображабщего объект
        :return: str
        """
        def str_value(key):
            return f'"{self.column_str(key)(r[key])}"'

        r = self._dict()
        return '{' + ','.join([':'.join([f'"{key}"', str_value(key)]) for key, value in r.items()]) + '}'

    @classmethod
    def of(cls, obj):
        """
        Возвращает все объекты класса cls, относящиеся к объекту obj
        :param obj: _DBObject
        """
        raise NotImplementedError(cls)

    @classmethod
    def new(cls, session=None, **kwargs):
        """
        Создает новый элемент и присодияет его к сессии
        :param session: ISession
        :param kwargs: dict
        :return: _DBObject
        """
        obj = cls(**kwargs)
        if session is not None:
            session.add(obj)
        return obj

    @classmethod
    def table(cls):
        """
        Возвращает объект, представляющий таблицу класса cls
        :return: Table
        """
        return cls.__table__

    @classmethod
    def insert_or_ignore(cls, data: List[Dict[str, Any]]):
        """
        Вставляет в таблицу записи, при совпадении - игнорирует
        :param data: Список словарей {название_атрибута: значение}
        """
        cls.table().insert(
            prefixes=['OR IGNORE']
        ).execute(data)

    @classmethod
    def get(cls, session: ISession = None, **kwargs) -> '_DBObject':
        """
        Производит поиск элмента по заданным в **kwargs атрубтам и возвращает найденные строки
        :param session: ISession
        :param kwargs: dict
        :return: _DBObject
        """
        if session is None:
            session = Session()
        return session.query(cls).filter_by(**kwargs).first()

    @classmethod
    def get_or_create(cls, session: ISession = None, **kwargs):
        """
        Производит поиск элмента по заданным в **kwargs атрубтам и возвращает найденные поля,
        если записей не найдено, то создаёт запись
        :param session: ISession
        :param kwargs: dict
        :return: _DBObject
        """
        if session is None:
            session = Session()
        instance = cls.get(session, **kwargs)
        if instance is not None:
            return instance
        else:
            params = dict((k, v) for k, v in kwargs.items() if not isinstance(v, ClauseElement))
            instance = cls(**params)
            session.add(instance)
            return instance

    @classmethod
    def class_(cls, name) -> Type['_DBObject']:
        """
        Воспроизводит класс по его названию
        :param name: имя класса
        :return: Type
        """
        return eval(name)

    def __eq__(self, other):
        if isinstance(other, _DBObject):
            return super().__eq__(other)

        if isinstance(other, dict):
            return self._dict() == other

        super().__eq__(other)

    @classmethod
    def subclasses(cls) -> List[Type['_DBObject']]:
        """
        :return: list of real subclasses
        """
        return list(
            filter(
                lambda x: '_' != x.__name__[0],
                set(cls.__subclasses__()).union([s for c in cls.__subclasses__() for s in c.subclasses()])))

    def session(self) -> ISession:
        """
        Возвращает сессию, которой принадлежит объект
        :return: ISession
        """
        return inspect(self).session

    def __str__(self):
        if hasattr(self, 'name'):
            return self.name
        if hasattr(self, 'full_name'):
            return self.full_name()


class _DBTrackedObject(_DBObject):
    _created = Column(DateTime, default=datetime.now)
    _updated = Column(DateTime, default=datetime.now, onupdate=datetime.now)
    _is_deleted = Column(Boolean, default=False)
    _deleted = Column(DateTime)

    def delete(self):
        """
        помечает себя как удаленный
        """
        self._is_deleted = True
        self._deleted = datetime.now()

    def restore(self):
        """
        восстанавливает себя
        """
        self._deleted = None
        self._is_deleted = False

    def is_deleted(self):
        """
        Сообщает удален ли элемент
        :return: bool
        """
        return self._is_deleted


class _DBPerson(_DBTrackedObject):
    type_name: str

    last_name = Column(String(50), nullable=False)
    first_name = Column(String(50), nullable=False)
    middle_name = Column(String(50), default="")
    sex = Column(Boolean, default=True)
    email = Column(String(200))
    _card_id = Column('card_id', String(16), unique=True)

    _auth = None

    def __init__(self, **kwargs):
        super().__init__(
            last_name=kwargs.pop('last_name', ''),
            first_name=kwargs.pop('first_name', ''),
            middle_name=kwargs.pop('middle_name', ''),
            sex=kwargs.pop('sex', True),
            email=kwargs.pop('email', ''),
            **kwargs)

    @property
    def card_id(self) -> Integer:
        """
        Свойство идентификатор карты
        :return: int
        """
        return Get.card_id(self._card_id)

    @card_id.setter
    def card_id(self, value: str or int):
        self._card_id = Get.card_id(value)

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
            return user
        else:
            raise ValueError('user of {id} not found'.format(id=id))

    def full_name(self, case=None):
        """
        Возвращает полное имя
        :param case: падеж, по умолчанию Именительный
        :return: str
        """
        from Domain.functools.Format import format_name
        return format_name(self, case)

    @property
    def auth(self):
        """
        @Свойство указатель на объект-аутентификацию
        Если оно не присвоено объекту, то вызывается исключение Неаутентифициорованного пользователя
        :return: Auth
        """
        if hasattr(self, '_auth') and self._auth is not None:
            return self._auth
        raise UnauthorizedError()


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
                obj.session() \
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
                obj.session()
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
            return obj.session() \
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
        if isinstance(obj, (list, _AssociationList, frozenset)):
            return DBList([Visitation.of(sub_obj) for sub_obj in obj], flat=True, unique=True,
                          with_deleted=with_deleted)

        if isinstance(obj, (Student, Lesson)):
            return DBList(obj.visitations, with_deleted=with_deleted)

        if isinstance(obj, Group):
            return DBList(Visitation.of(obj.students), flat=True, with_deleted=with_deleted)

        if isinstance(obj, (Professor, Discipline)):
            return DBList([sub_obj.visitations for sub_obj in obj.lessons], flat=True, with_deleted=with_deleted)

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

    class Type:
        STUDENT = 0
        PROFESSOR = 1
        PARENT = 2
        ADMIN = 3

    __tablename__ = 'auth5'

    login = Column(String(40), unique=True)
    password = Column(String(40))
    uid = Column(String(40), unique=True)
    user_type = Column(Integer)
    user_id = Column(Integer)

    __user = None

    @property
    def user(self) -> Union['Student', 'Professor']:
        """

        :return: Professor or Student
        """
        if self.__user is None:
            if self.user_type == Auth.Type.STUDENT:
                self.__user: Student = self.session() \
                    .query(Student) \
                    .filter(Student.id == self.user_id) \
                    .first()
            elif self.user_type == Auth.Type.PROFESSOR:
                self.__user: Professor = self.session() \
                    .query(Professor) \
                    .filter(Professor.id == self.user_id) \
                    .first()
                self.__user._auth = self

        return self.__user

    @staticmethod
    def log_in(login=None, password=None, **kwargs) -> 'Auth':
        """

        Производит аутентифкацию в двухфакторном режиме

        :param login: логин (открытый ключ)
        :param password: пароль (секретный ключ)
        :return: учетную запись пользователя
        """
        sess = Session()

        query = sess.query(Auth).filter(Auth.login == login)
        if query.first():
            auth = query.filter(Auth.password == password).first()
            if auth:
                return auth
            raise InvalidPasswordException()
        raise InvalidLoginException()

    @staticmethod
    def log_in_by_uid(uid):
        sess = Session()

        auth = sess.query(Auth).filter(Auth.uid == uid).first()
        if auth:
            return auth
        raise InvalidUidException()

    def __repr__(self):
        return f"<Auth(id={self.id}," \
            f" user_type={self.user_type}," \
            f" user_id={self.user_id})>"

    def data(self) -> Dict[str, str]:
        return {
            'login': self.login,
            'password': self.password,
            'user_type': self.user_type
        }


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
            return DBList([Discipline.of(sub_obj) for sub_obj in obj], flat=True, unique=True)

        if isinstance(obj, Lesson):
            return DBList([obj.discipline], with_deleted=with_deleted)

        if isinstance(obj, Professor):
            return DBList([lesson.discipline for lesson in obj.lessons], flat=True, unique=True,
                          with_deleted=with_deleted)

        raise NotImplementedError(type(obj))


class Lesson(Base, _DBTrackedObject):
    """
    Lesson
    """

    class Type(_ListedValues):
        Lecture = 0
        Lab = 1
        Practice = 2

        __values__ = {
            Lecture: "Лекция",
            Practice: "Практика",
            Lab: "Лабораторная работа"
        }

        def __init__(self, *args):
            super().__init__()

        def __str__(self):
            return self.__values__[self]

        @classmethod
        def from_str(cls, string: str):
            for key, value in cls.__values__.items():
                if value == string:
                    return cls(key)
            else:
                raise ValueError(f'no such case: {string}')

    __tablename__ = 'lessons'
    __table_args__ = (
        UniqueConstraint('professor_id', 'date', name='lesson_UK'),
        _DBObject.__table_args__
    )

    professor_id: int = Column(Integer, ForeignKey('professors.id'), nullable=False)
    discipline_id: int = Column(Integer, ForeignKey('disciplines.id'), nullable=False)
    _type: int = Column('type', Integer, nullable=False, default=Type.Lecture)
    date: datetime = Column(DateTime, nullable=False)
    completed: bool = Column(Boolean, nullable=False, default=False)
    room_id: str = Column(String(40), nullable=False)

    @property
    def type(self) -> 'Lesson.Type':
        return self.Type(self._type)

    @type.setter
    def type(self, value: 'Lesson.Type' or int or str):
        if isinstance(value, int):
            self._type = value
        elif isinstance(value, str):
            int_value = Get.int(value)
            if int_value is not None:
                self._type = int_value
            else:
                self._type = Lesson.Type.from_str(value)

    _groups = relationship('LessonsGroups', backref=backref('lesson'))
    groups = association_proxy('_groups', 'group',
                               creator=lambda group: LessonsGroups(group=group))

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

    def repr(self):
        from Domain.Data import names_of_groups

        return f"""{self.type} {self.date}
        дисциплина: {self.discipline.name}
        преподаватель: {self.professor.full_name()}
        группы: {names_of_groups(self.groups)}
        кабинет: {self.room_id}"""

    @classmethod
    def of(cls, obj, intersect=False, with_deleted=False) -> List['Lesson']:
        """

        :param intersect:
        :param obj: объект или спсиок объектов базы данных
        :param with_deleted: включать ли в список удаленные объекты
        :return: список родителей, отоносящихся к объекту
        """
        if isinstance(obj, (list, _AssociationList, frozenset)):
            if intersect:
                lessons = None
                for sub_obj in obj:
                    lessons = Lesson.of(sub_obj) \
                        if lessons is None \
                        else list(set(lessons).intersection(Lesson.of(sub_obj)))
                return DBList(lessons,
                              with_deleted=with_deleted,
                              flat=True)

            else:
                return DBList([Lesson.of(sub_obj) for sub_obj in obj],
                              flat=True,
                              unique=True,
                              with_deleted=with_deleted)

        if isinstance(obj, (Professor, Discipline, Group)):
            return DBList(obj.lessons,
                          with_deleted=with_deleted)

        if isinstance(obj, Student):
            return DBList([Lesson.of(sub_obj) for sub_obj in obj.groups],
                          flat=True,
                          with_deleted=with_deleted)

        raise NotImplementedError(type(obj))


class Administration(Base, _DBPerson):
    """
    Таблица администраций
    """
    __tablename__ = 'administrations'
    type_name = 'Представитель администрации'

    notification = relationship('NotificationParam', backref=backref("admin", cascade="all,delete"),
                                passive_updates=False)
    professors = association_proxy('notification', 'professor')

    def __repr__(self):
        return f"<Administration(id={self.id}, card_id={self.email}, " \
            f"last_name={self.last_name}, first_name={self.first_name}, " \
            f"middle_name={self.middle_name})>"

    @classmethod
    @filter_deleted
    @listed
    def of(cls, obj, with_deleted=False) -> List['Administration']:
        """
        Возвращает список Администраторов, которые относятся к переданому объекту
        :param obj: Объект базы данных
        :param with_deleted: список включает удаленные объекты
        :return: список
        """
        if isinstance(obj, Professor):
            return obj.admins

        if isinstance(obj, NotificationParam):
            return [obj.admin]

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

        raise NotImplementedError(type(obj))


class Professor(_DBPerson, Base):
    """
    Таблица преподавателей
    """
    __tablename__ = 'professors'
    type_name = 'Преподаватель'

    _last_update_in = Column(DateTime, default=datetime.now)
    _last_update_out = Column(DateTime)

    lessons: List[Lesson] = relationship("Lesson", backref=backref('professor'), order_by="Lesson.date")

    _admins = relationship('NotificationParam', backref="professor")
    admins = association_proxy('_admins', 'admin')

    _auth: Auth = None

    def groups(self, with_deleted=False) -> List[List['Group']]:
        return [list(item)
                for item in set([frozenset(filter(lambda group: not group._is_deleted | with_deleted, lesson.groups))
                                 for lesson in self.lessons])]

    @classmethod
    @filter_deleted
    @listed
    def of(cls, obj, with_deleted=False) -> List['Professor']:
        """

        :param obj: объект или спсиок объектов базы данных
        :param with_deleted: включать ли в список удаленные объекты
        :return: список преподавателей, отоносящихся к объекту
        """
        if isinstance(obj, (Lesson, NotificationParam)):
            return [obj.professor]

        if isinstance(obj, Visitation):
            return [lesson.professor for lesson in obj.lesson]

        if isinstance(obj, Administration):
            return obj.professors

        if isinstance(obj, Student):
            return Professor.of(obj.groups, with_deleted=with_deleted)

        if isinstance(obj, Group):
            return Professor.of(obj.lessons, with_deleted=with_deleted)

        if isinstance(obj, Professor):
            return DBList([obj])

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

        classes = _DBTrackedObject.subclasses()

        if Auth in classes:
            classes.remove(Auth)
        if Professor in classes:
            classes.remove(Professor)

        for class_ in classes:
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
    show_groups = Column(Boolean, default=False)
    show_disciplines = Column(Boolean, default=False)
    show_students = Column(Boolean, default=True)
    show_progress = Column(Boolean, default=False)

    @classmethod
    @filter_deleted
    @listed
    def of(cls, obj, with_deleted=False) -> List['NotificationParam']:
        """

        :param obj: Объект базы данных или список объектов
        :param with_deleted: включать ли в список удаленные объекты
        :return: список Парааметров оповещений, которые отностятся к переданному объекту
        """

        if isinstance(obj, Professor):
            return obj._admins

        if isinstance(obj, Administration):
            return obj.notification

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
    @filter_deleted
    @listed
    def of(cls, obj, flat_list=False) -> List['Group'] or List[List['Group']]:
        """

        :param flat_list: исключить из результата наборы групп (оставить только перечень групп)
        :param obj: объект или спсиок объектов базы данных
        :param with_deleted: включать ли в список удаленные объекты
        :return: список групп, отоносящихся к объекту
        """

        if isinstance(obj, Lesson):
            return obj.groups

        if isinstance(obj, Discipline):
            return [Group.of(lesson) for lesson in obj.lessons]

        if isinstance(obj, Student):
            return obj.groups

        if isinstance(obj, Professor):
            return obj.groups()

        raise NotImplementedError(type(obj))


class Student(Base, _DBPerson):
    """
    Таблица студентов
    """
    type_name = 'Студент'

    __tablename__ = 'students'

    _parents = relationship('StudentsParents', backref=backref('student'))
    parents = association_proxy('_parents', 'parent')

    _groups = relationship('StudentsGroups', backref=backref('student'))
    groups = association_proxy('_groups', 'group', creator=lambda group: StudentsGroups(group=group))

    visitations = relationship("Visitation", backref=backref('student'))

    def __repr__(self):
        return f"<Student(id={self.id}, card_id={self.card_id}," \
            f" last_name={self.last_name}, first_name={self.first_name}, " \
            f"middle_name={self.middle_name})>"

    @classmethod
    @filter_deleted
    @listed
    def of(cls, obj, with_deleted=False) -> List['Student']:
        """

        :param obj: объект или спсиок объектов базы данных
        :param with_deleted: включать ли в список удаленные объекты
        :return: список студентов, отоносящихся к объекту
        """

        if isinstance(obj, Group):
            return sorted(obj.students, key=lambda student: student.last_name)

        if isinstance(obj, Lesson):
            return [Student.of(group) for group in obj.groups]

        if isinstance(obj, (Professor, Discipline)):
            return [Student.of(lesson.groups) for lesson in obj.lessons]

        raise NotImplementedError(type(obj))


class Parent(Base, _DBPerson):
    """
    Таблица содержащая информациюо родителях
    """
    __tablename__ = "parents"
    type_name = "Родитель"

    _students = relationship("StudentsParents", backref=backref('parent'))
    students = association_proxy('_students', 'student')

    @classmethod
    @listed
    def of(cls, obj, with_deleted=False) -> List['Parent']:
        """

        :param obj: объект или спсиок объектов базы данных
        :param with_deleted: включать ли в список удаленные объекты
        :return: список родителей, отоносящихся к объекту
        """

        if isinstance(obj, Student):
            return obj.parents

        if isinstance(obj, Professor):
            return Parent.of(Student.of(obj))

        raise NotImplementedError(type(obj))


if _new:
    Base.metadata.create_all(engine)
else:
    try:
        p = Auth.log_in_by_uid(-1)
    except:
        Base.metadata.create_all(engine)
