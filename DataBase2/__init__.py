"""

Файл с описанием базы данных
"""
import enum
import os
import sys
from datetime import datetime, timedelta
from inspect import isclass
from pathlib import Path
from typing import List, Union, Dict, Any, Type, Callable, Set
from warnings import warn

from math import floor
from sqlalchemy import create_engine, UniqueConstraint, Column, Integer, \
    String, ForeignKey, Boolean, DateTime, inspect, Enum, Binary, LargeBinary
from sqlalchemy.ext.associationproxy import association_proxy
from sqlalchemy.ext.declarative import declarative_base, declared_attr
from sqlalchemy.orm import sessionmaker, relationship, scoped_session, backref
from sqlalchemy.pool import StaticPool, QueuePool
from sqlalchemy.sql import ClauseElement
from sqlalchemy.util import ThreadLocalRegistry

from DataBase2.SessionInterface import ISession
from Domain.ArgPars import get_argv
from Domain.Exception.Authentication import InvalidPasswordException, \
    InvalidLoginException, InvalidUidException, \
    UnauthorizedError
from Domain.Validation.Values import Get
from Domain.functools.Decorator import listed, filter_deleted, sorter, \
    is_iterable, filter_semester
from Parser import IJSON

try:
    _root = sys.modules['__main__'].__file__
except AttributeError:
    _root = "run_client.py"

_root = os.path.basename(_root)
_new = False


def make_database_file(path: Path):
    """
    Проверяет создан ли файл базы данных

    :param path: путь к файлу базы данных
    :return: прилось ли создавать новый файл
    """
    if path.exists():
        return False

    path_to_create = []

    parent_path: Path = path.parent
    while not parent_path.exists():
        path_to_create.append(parent_path)

    for pp in path_to_create:
        pp.mkdir()

    fh = open(str(path), 'w+')
    fh.close()
    return True


_is_mysql = _root != 'run_client.py' and os.name != 'nt'
if _is_mysql:
    from DataBase2.config2 import Config

    engine = create_engine(Config.connection_string,
                           pool_pre_ping=False,
                           echo=False,
                           poolclass=QueuePool,
                           pool_recycle=3600,
                           connect_args=dict(use_unicode=True))

else:
    db_path = Path(__file__).parent / 'db2.db'
    connection_string = 'sqlite:///{}'.format(db_path)

    _new = make_database_file(db_path)

    engine = create_engine(connection_string,
                           echo=True if get_argv('--db-echo') else False,
                           poolclass=StaticPool,
                           connect_args={'check_same_thread': False})

Base = declarative_base(bind=engine)

if _is_mysql:
    Session = ThreadLocalRegistry(sessionmaker(bind=engine, autoflush=False, expire_on_commit=False))
else:
    Session = scoped_session(sessionmaker(bind=engine, autoflush=False, expire_on_commit=False))

metadata = Base.metadata

Session: Callable[[], ISession] = Session


def is_none(x):
    """
    Проверяет значение x на None во всех возможных формах

    :param x: Any
    :return: bool
    """
    return x in {None, 'None', 'null'}


def name(obj):
    """
    Возвращает удобочитаемое описание объекта
    :param obj: объект
    :return: строка
    """
    if isinstance(obj, enum.Enum):
        return obj.value
    if is_iterable(obj):
        return ', '.join([name(o) for o in obj])
    if isinstance(obj, _DBNamed):
        return obj.full_name()
    if isclass(obj) and issubclass(obj, _DBNamed):
        return obj.type_name
    return str(obj)


class _DBObject(IJSON):
    __tablename__: str
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
                if is_none(x):
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
            if len(name) < 16
        }

    def dict(self):
        """
        Возвращает словарь {атрибут:значение} всех полей записи таблицы
        :return:
        """
        return {key: item for key, item in self._dict().items() if key[0] != '_'}

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
    @listed
    def of(cls, obj, *args, **kwargs):
        """
        Возвращает все объекты класса cls, относящиеся к объекту obj
        :param obj: _DBObject
        """
        if hasattr(obj, cls.__name__.lower()):
            warn(f'you mast declare relation between `{cls.__name__}` and `{type(obj).__name__}` directly')
            res = getattr(obj, cls.__name__.lower())
            if not is_iterable(res):
                return [res]
            return res

        if hasattr(obj, cls.__name__.lower() + 's'):
            warn(f'you mast declare relation between `{cls.__name__}` and `{type(obj).__name__}` directly')
            res = getattr(obj, cls.__name__.lower() + 's')
            if not is_iterable(res):
                return [res]
            return res

        raise NotImplementedError(f'{cls.__name__}.of({type(obj)})')

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
        # TODO сделать обработку на клиенте измененной БД
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
        return self.__repr__()


class _Displayable:
    def __gt__(self, other):
        """
        Сравнивает названия объектов для их отображения в ComboBox в алфавитном порядке
        :param other: другой объект
        :return: bool
        """
        return name(self) > name(other)


class _DBRoot(_Displayable):
    type_name: str


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

    def __bool__(self):
        return not self._is_deleted


class _DBNamed(_DBObject):
    type_name: str

    def full_name(self, case=None) -> str:
        raise NotImplementedError()

    def short_name(self) -> str:
        warn('short name is not define')
        return self.full_name()

    def __repr__(self):
        return f"<{type(self).__name__} (name={self.full_name()})>"


class _DBNamedObject(_DBNamed):
    type_name: str
    name: str = Column(String(100), nullable=False)
    abbreviation: str = Column(String(16))

    def full_name(self, case=None) -> str:
        from Domain.functools.Format import inflect
        if case is not None:
            if self.type_name in self.name:
                name = f"{inflect(self.type_name, case)}{self.name.replace(self.type_name, '')}"
            else:
                name = f"{inflect(self.type_name, case)}{self.name}"
        else:
            name = self.name
        return name.title()

    def short_name(self) -> str:
        if is_none(self.abbreviation):
            return self.name
        return self.abbreviation

    @classmethod
    def get(cls, session=None, **kwargs):
        if 'name' in kwargs.keys():
            return session.query(cls).filter(cls.name == kwargs.get('name')).first()
        else:
            return super().get(session, **kwargs)


class _DBEmailObject(_DBNamed):
    @declared_attr
    def contact_info_id(cls) -> int:
        return Column(Integer, ForeignKey('contacts.id'))

    @declared_attr
    def contact(cls) -> 'ContactInfo':
        return relationship('ContactInfo')

    @classmethod
    def email_subclasses(cls) -> List[Type['_DBEmailObject']]:
        res = [cls]
        for class_ in cls.__subclasses__():
            res.extend(class_.email_subclasses())
        return res

    def appeal(self, case: set = None) -> str:
        raise NotImplementedError()

    def has_lessons_since(self, td: timedelta or datetime) -> bool:
        now = datetime.now()
        if isinstance(td, timedelta):
            since = now - td
        elif isinstance(td, datetime):
            since = td
        else:
            raise NotImplementedError(type(td))

        for l in Lesson.of(self):
            if since < l.date < now:
                return True
        return False


class _DBPerson(_DBEmailObject, _DBTrackedObject):
    type_name: str

    last_name: str = Column(String(50), nullable=False)
    first_name: str = Column(String(50), nullable=False)
    middle_name: str = Column(String(50), default="")
    _card_id = Column('card_id', String(16), unique=True)

    _auth = None

    def appeal(self, case=None):
        if case is not None:
            from Domain.functools.Format import inflect
            return f"{inflect(self.type_name, case)} {self.full_name(case)}"
        else:
            return f"{self.type_name} {self.full_name()}"

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
        from Domain.functools.Format import inflect
        if is_none(self.middle_name):
            name = f"{self.last_name} {self.first_name}"
        else:
            name = f'{self.last_name} {self.first_name} {self.middle_name}'

        if case is not None:
            name = inflect(name, case)

        return name.title()

    def short_name(self):
        return f'{self.last_name} {self.first_name[0]}.' + (f' {self.middle_name[0]}.' if len(self.middle_name) else '')

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

    @classmethod
    def get(cls, session: ISession = None, **kwargs):
        if session is None:
            session = Session()
        return session.query(cls).filter(cls.id == kwargs.get('id')).first()


class _DBList:
    @classmethod
    def all(cls, session: ISession = None):
        if session is None:
            session = Session()
        return session.query(cls).all()


class ContactInfo(Base, _DBTrackedObject):
    __tablename__ = "contacts"

    email = Column(String(200))

    auto = Column(Boolean, default=False)
    last_auto = Column(DateTime)
    interval_auto_hours = Column(Integer)

    _views = relationship('ContactViews', backref='contact')
    views: List['DataView'] = association_proxy('_views', '_view', creator=lambda x: ContactViews(_view=x))

    def start_auto(self, target_time: datetime.time, interval_hours: int):
        self.auto = True
        now = datetime.now()
        self.last_auto = datetime(now.year, now.month, now.day) + target_time
        self.interval_auto_hours = interval_hours

    def stop_auto(self):
        self.auto = False

    @classmethod
    @listed
    def of(cls, obj, *args, **kwargs):
        if isinstance(obj, Professor):
            return [obj.contact] if obj.contact is not None else []

        raise NotImplementedError(type(obj))


class DataView(Base, _DBNamedObject, _DBList):
    # TODO _TRACKED
    __tablename__ = "data_views"

    script_path = Column(String(500))

    @classmethod
    @listed
    def of(cls, obj, *args, **kwargs):
        if isinstance(obj, (Professor)):
            return DataView.of(ContactViews.of(obj))

        if isinstance(obj, ContactViews):
            return obj._view

        if isinstance(obj, ContactInfo):
            return DataView.of(ContactViews.of(obj))

        return obj.session().query(DataView).all()


class ContactViews(Base, _DBTrackedObject):
    __tablename__ = 'emails_views'
    __table_args__ = (
        UniqueConstraint('contact_info_id', 'data_view_id', name='contact_views_UK'),
        _DBObject.__table_args__,
    )

    contact_info_id = Column(Integer, ForeignKey('contacts.id'))
    data_view_id = Column(Integer, ForeignKey('data_views.id'))

    _view = relationship('DataView')

    @classmethod
    @filter_deleted
    @listed
    def of(cls, obj, *args, **kwargs):
        if isinstance(obj, Professor):
            return ContactViews.of(ContactInfo.of(obj))

        if isinstance(obj, ContactInfo):
            return obj._views

        if isinstance(obj, DataView):
            return ContactViews.of()

        raise NotImplementedError(type(obj))


class Faculty(Base, _DBEmailObject, _DBNamedObject, _DBList, _DBRoot):
    __tablename__ = "faculties"
    type_name = "Факультет"

    def appeal(self, case=None):
        if case is not None:
            from Domain.functools.Format import inflect
            return f"{inflect('методист', case)} {self.full_name({'gent'})}"
        else:
            return f"методист {self.full_name({'gent'})}"

    groups: List['Group'] = relationship('Group', backref=backref('faculty'))
    admins: List['Administration'] = association_proxy('_admins', 'admin')

    @classmethod
    @listed
    def of(cls, obj, *args, **kwargs) -> List['Faculty']:
        if isinstance(obj, Student):
            return Faculty.of(Group.of(obj))

        if isinstance(obj, Group):
            return [obj.faculty]

        if isinstance(obj, Discipline):
            return Faculty.of(obj.department)

        if isinstance(obj, Department):
            return [obj.faculty]

        if isinstance(obj, (Professor, Semester, Room)):
            return Faculty.of(obj.lessons)

        if isinstance(obj, Lesson):
            return Faculty.of(obj.groups)

        if isinstance(obj, Faculty):
            return [obj]

        if isinstance(obj, Administration):
            return obj.faculties

        raise NotImplementedError(type(obj))

    def __gt__(self, other):
        return self.full_name() > other.full_name()


class FacultyAdministrations(Base, _DBObject):
    __tablename__ = "faculty_administrations"

    faculty_id = Column('Faculty', ForeignKey('faculties.id'))
    admin_id = Column('Administration', ForeignKey('administrations.id'))

    faculty: Faculty = relationship('Faculty', backref=backref('_admins'))
    admin: 'Administration' = relationship('Administration', backref=backref('_faculties'))

    @classmethod
    @listed
    def of(cls, obj, *args, **kwargs):
        if isinstance(obj, Professor):
            raise UnauthorizedError()

        raise NotImplementedError(type(obj))


class Department(Base, _DBNamedObject, _DBEmailObject, _DBList, _DBRoot):
    __tablename__ = "departments"

    type_name = "Кафедра"

    faculty_id = Column(Integer, ForeignKey('faculties.id'), nullable=False)

    faculty: Faculty = relationship('Faculty', backref=backref('departments'))
    professors: List['Professor'] = association_proxy('_professors', 'professor')

    disciplines: List['Discipline']

    @classmethod
    @listed
    def of(cls, obj, *args, **kwargs):
        if isinstance(obj, Lesson):
            return Department.of(obj.professor)

        if isinstance(obj, Professor):
            return obj.departments

        if isinstance(obj, (Group, Room, Semester)):
            return Department.of(obj.lessons)

        if isinstance(obj, Student):
            return Department.of(Professor.of(obj))

        if isinstance(obj, Building):
            return Department.of(obj.rooms)

        raise NotImplementedError(type(obj))


class DepartmentProfessors(Base, _DBObject):
    __tablename__ = "departments_professors"
    __table_args__ = (
        UniqueConstraint('department_id', 'professor_id', name='departments_professors_UK'),
        _DBObject.__table_args__
    )

    department_id = Column(Integer, ForeignKey('departments.id'))
    professor_id = Column(Integer, ForeignKey('professors.id'))

    department = relationship('Department', backref=backref('_professors'))
    professor = relationship('Professor', backref=backref('_department'))

    @classmethod
    @listed
    def of(cls, obj, *args, **kwargs):
        if isinstance(obj, Professor):
            return obj._department

        raise NotImplementedError(type(obj))


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
    @listed
    def of(cls, obj, *args, **kwargs):
        if isinstance(obj, Professor):
            return StudentsGroups.of(Group.of(obj))
        if isinstance(obj, Group):
            return obj._students
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
    @filter_deleted
    @listed
    def of(cls, obj, *args, **kwargs):
        if isinstance(obj, Professor):
            return LessonsGroups.of(Group.of(obj))
        if isinstance(obj, Group):
            return obj._lessons
        raise NotImplementedError(type(obj))


class Building(Base, _DBNamed, _DBList, _DBRoot):
    __tablename__ = 'building'
    type_name = 'Корпус'
    address = Column(String(500))
    abbreviation = Column(String(16))

    @classmethod
    @listed
    def of(cls, obj, *args, **kwargs):
        if isinstance(obj, Lesson):
            return [obj.room.building]

        if isinstance(obj, (Professor, LessonType, Group, LessonType)):
            return Building.of(obj.lessons)

        if isinstance(obj, Student):
            return Building.of(obj.groups)

        if isinstance(obj, Room):
            return [obj.building]

        raise NotImplementedError(type(obj))

    def short_name(self):
        return self.abbreviation

    def full_name(self, case=None):
        return self.address


class Room(Base, _DBNamed, _DBRoot):
    __tablename__ = 'room'
    type_name = 'Аудитория'
    building_id = Column(Integer, ForeignKey('building.id'))
    room_number = Column(Integer)
    reader_id = Column(Integer)

    building: Building = relationship('Building', backref=backref('rooms'))

    def full_name(self, case=None):
        return f'{self.room_number}/{self.building.short_name()}'

    @classmethod
    @listed
    def of(cls, obj, *args, **kwargs):
        if isinstance(obj, Lesson):
            return [obj.room]

        if isinstance(obj, (Professor, Room, LessonType, Group, Semester)):
            return Room.of(obj.lessons)

        if isinstance(obj, Student):
            return Room.of(obj.groups)

        if isinstance(obj, Department):
            return Room.of(obj.professors)

        if isinstance(obj, Building):
            return obj.rooms

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
    @listed
    def of(cls, obj, *args, **kwargs):
        if isinstance(obj, Professor):
            return StudentsParents.of(Student.of(obj))
        if isinstance(obj, Student):
            return obj._parents
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
    @filter_semester
    @filter_deleted
    @listed
    def of(cls, obj, *args, **kwargs) -> List['Visitation']:
        """

        :param obj: объект или список объектов базы данных
        :return: список посещений объекта
        """

        if isinstance(obj, (Student, Lesson)):
            return obj.visitations

        if isinstance(obj, Group):
            return Visitation.of(obj.students)

        if isinstance(obj, (Professor, Discipline, Faculty, Department, Room)):
            return Visitation.of(Lesson.of(obj))

        if isinstance(obj, (Semester, Room, LessonType)):
            return Visitation.of(obj.lessons)

        if isinstance(obj, Building):
            return Visitation.of(obj.rooms)

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


class LossReason(enum.Enum):
    sick = 'Болезнь'
    work = 'Работа'
    science = 'Научная деятельность'
    other = 'Другое'


class VisitationLossReason(Base, _DBTrackedObject):
    __tablename__ = "loss_reason"
    __table_args__ = (
        UniqueConstraint('lesson_id', 'student_id', name='loss_reason_UK'),
        _DBObject.__table_args__,
    )

    id = Column(Integer, primary_key=True)
    lesson_id = Column(Integer, ForeignKey('lessons.id'))
    student_id = Column(Integer, ForeignKey('students.id'))
    reason = Column(Enum(LossReason), nullable=False)
    file_ext = Column(String(10))
    file = Column(LargeBinary)

    student = relationship('Student', backref=backref('loss_reasons'))
    lesson = relationship("Lesson", backref=backref('loss_reasons'))

    def set_file(self, path:Path):
        with open(str(path), 'rb') as file:
            data = file.read()

            if self.file != data:
                self.file = data
            suffix = path.suffix[1:] if path.suffix.startswith('.') else path.suffix
            if self.file_ext != suffix:
                self.file_ext = suffix


class UserType(int):
    STUDENT = 0
    PROFESSOR = 1
    PARENT = 2
    ADMIN = 3


class Auth(Base, _DBTrackedObject):
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


class Discipline(Base, _DBTrackedObject, _DBNamedObject, _DBRoot):
    """
    Таблица дисциплин
    """
    __tablename__ = 'disciplines'
    type_name = "Дисциплина"

    department_id = Column(Integer, ForeignKey('departments.id'))
    department: Department = relationship('Department', backref=backref('disciplines'))

    lessons: List['Lesson'] = relationship('Lesson', backref=backref('discipline'))

    # department: Department

    def __repr__(self):
        return f"<Discipline(id={self.id}," \
            f" name={self.name})>"

    @classmethod
    @filter_deleted
    @filter_semester
    @listed
    def of(cls, obj, *args, **kwargs) -> List['Discipline']:
        """

        :param obj: объект или список объектов базы данных
        :return: список дисциплин объекта
        """
        if isinstance(obj, Lesson):
            return [obj.discipline]

        if isinstance(obj, (Professor, Room, Group, LessonType)):
            return Discipline.of(obj.lessons)

        if isinstance(obj, Student):
            return Discipline.of(obj.groups)

        if isinstance(obj, Building):
            return Discipline.of(obj.rooms)

        if isinstance(obj, Department):
            return obj.disciplines

        if isinstance(obj, Discipline):
            return [obj]

        raise NotImplementedError(type(obj))


class Semester(Base, _DBNamed, _DBRoot):
    __tablename__ = "semesters"
    type_name = 'Семестр'

    start_date: datetime = Column(DateTime, nullable=False, unique=True)
    first_week_index: int = Column(Integer, default=0, nullable=False)

    def full_name(self, case=None):
        if 1 < self.start_date.month < 9:
            return f'2 семестр {self.start_date.year - 1}-{self.start_date.year}'
        else:
            return f'1 семестр {self.start_date.year}-{self.start_date.year + 1}'

    @classmethod
    @listed
    def of(cls, obj, *args, **kwargs):
        if isinstance(obj, Lesson):
            return [obj.semester]

        if isinstance(obj, (Professor, Discipline, Group)):
            return Semester.of(obj.lessons)

        if isinstance(obj, Student):
            return Semester.of(obj.groups)

        if isinstance(obj, (Department, Faculty)):
            return Semester.of(Lesson.of(obj))

        if isinstance(obj, Semester):
            return [obj]

        if isinstance(obj, Visitation):
            return Semester.of(obj.lesson)

        raise NotImplementedError(type(obj))

    def __gt__(self, other):
        return self.start_date > other.start_date

    @classmethod
    def current(cls, obj) -> 'Semester':
        """

        Выбирает текущий семестр для любого объекта из списка занятий объекта по следующим правилам:
            - дата занятия не превышает текущую дату;
            - дата занятия максимальна.

        :param obj: _DBObject
        :return: Semester
        """
        now = datetime.now()
        max: Lesson = None
        for lesson in Lesson.of(obj):
            if max is None or (lesson.date < now and lesson.date > max.date):
                max = lesson

        return max.semester

    @staticmethod
    def closest_semester_start(now=None):
        if now is None:
            now = datetime.now()
        year = now.year
        month = now.month

        if month > 6:
            return datetime(year, 9, 1)
        else:
            temp = datetime(year, 2, 7)
            temp += timedelta(7 - temp.weekday())
            return temp


class LessonType(Base, _DBNamedObject, _DBList, _DBRoot):
    __tablename__ = 'lesson_type'
    type_name = 'Вид занятия'

    @classmethod
    @listed
    def of(cls, obj, *args, **kwargs):
        if isinstance(obj, (Professor, Room, Semester, Discipline, Group)):
            return LessonType.of(obj.lessons)

        if isinstance(obj, Student):
            return LessonType.of(obj.groups)

        if isinstance(obj, Lesson):
            return [obj.type]

        if isinstance(obj, LessonType):
            return [obj]

        raise NotImplementedError(type(obj))


class Lesson(Base, _DBTrackedObject, _Displayable):
    """
    Lesson
    """

    __tablename__ = 'lessons'
    __table_args__ = (
        UniqueConstraint('professor_id', 'date', name='lesson_UK'),
        _DBObject.__table_args__
    )

    professor_id: int = Column(Integer, ForeignKey('professors.id'), nullable=False)
    discipline_id: int = Column(Integer, ForeignKey('disciplines.id'), nullable=False)
    type_id: int = Column(Integer, ForeignKey('lesson_type.id'), nullable=False)
    date: datetime = Column(DateTime, nullable=False)
    completed: bool = Column(Boolean, nullable=False, default=False)
    room_id: int = Column(Integer, ForeignKey('room.id'), nullable=False)
    semester_id = Column(Integer, ForeignKey('semesters.id'))
    semester: Semester = relationship('Semester', backref=backref('lessons'))

    discipline: Discipline

    room: Room = relationship('Room', backref=backref('lessons'))

    type: LessonType = relationship('LessonType', backref=backref('lessons'))

    _groups = relationship('LessonsGroups', backref=backref('lesson'))
    groups: List['Group'] = association_proxy('_groups', 'group',
                                              creator=lambda group: LessonsGroups(group=group))

    visitations = relationship('Visitation', backref=backref('lesson'))

    def __repr__(self):
        return f"<Lesson(id={self.id}, professor_id={self.professor_id}," \
            f" discipline_id={self.discipline_id}, " \
            f"date={self.date}, type={self.type.full_name()}," \
            f" completed={self.completed})>"

    _week = None

    @property
    def week(self):
        return floor((self.date - self.semester.start_date).days / 7) + self.semester.first_week_index

    def _name(self):
        return self.date.strftime("%Y.%m.%d %H:%M")

    def repr(self):
        from Domain.Data import names_of_groups

        return f"""{self.type.full_name()} {self.date}
        дисциплина: {self.discipline.name}
        преподаватель: {self.professor.full_name()}
        группы: {names_of_groups(self.groups)}
        кабинет: {self.room.short_name()}"""

    @classmethod
    @sorter
    @filter_deleted
    @filter_semester
    @listed
    def of(cls, obj, *args, **kwargs) -> List['Lesson']:
        """

        :param obj: объект или спсиок объектов базы данных
        :return: список родителей, отоносящихся к объекту
        """

        if isinstance(obj, (Professor, Discipline, Group)):
            return obj.lessons

        if isinstance(obj, (Student, Faculty)):
            return Lesson.of(obj.groups)

        if isinstance(obj, Department):
            return Lesson.of(Professor.of(obj))

        if isinstance(obj, (Semester, LessonType, Room)):
            return obj.lessons

        if isinstance(obj, Building):
            return Lesson.of(obj.rooms)

        if isinstance(obj, Lesson):
            return [obj]

        if isinstance(obj, Administration):
            return Lesson.of(obj.faculties)

        raise NotImplementedError(type(obj))

    @classmethod
    def intersect(cls, *args: _DBObject) -> Set['Lesson']:
        """
        Возвращает набор занятий, которые есть у всех переданных обьектов
        :param args: Любые сущности системы
        :return: Набор занятий
        """
        lsns = set()
        if len(args):
            lsns = set(Lesson.of(args[0]))
            for arg in args[1:]:
                lsns &= set(Lesson.of(arg))

        return lsns

    @staticmethod
    def filter_lessons(obj, lessons) -> List['Lesson']:
        """
        Возвращает список занятий, содержащий только занятия lessons и занятия принадлежащие к self
        :param obj:
        :param lessons:
        :return: Пересечение множества lessons и Lesson.of(obj)
        """
        if isclass(obj):
            return lessons

        if is_iterable(obj):
            return list(Lesson.intersect(*obj) & set(lessons))
        return [l for l in lessons if obj in type(obj).of(l)]

    @staticmethod
    def time_by_index(index: int) -> timedelta:
        """
        Возвращает время занятия по его индексу
        :param index: номер пары
        :return:
        """
        return [
            timedelta(0, 9 * 3600 + 0 * 60),
            timedelta(0, 10 * 3600 + 45 * 60),
            timedelta(0, 13 * 3600 + 0 * 60),
            timedelta(0, 14 * 3600 + 45 * 60),
            timedelta(0, 16 * 3600 + 20 * 60),
            timedelta(0, 18 * 3600 + 15 * 60),
        ][index]

    @staticmethod
    def index_by_time(time: datetime) -> int:
        """
        Возвращает номер пары по его времени
        :param time: время начала занятия
        :return: номер пары
        """
        if time.hour == 9:
            return 1
        elif time.hour == 10:
            return 2
        elif time.hour == 13:
            return 3
        elif time.hour == 14:
            return 4
        elif time.hour == 16:
            return 5
        elif time.hour == 18:
            return 6
        else:
            return -1

    def __gt__(self, other):
        return self.date > other.date

    def __str__(self):
        return f"{self.type.abbreviation} {self.date}"


class Administration(Base, _DBPerson):
    """
    Таблица администраций
    """
    __tablename__ = 'administrations'
    type_name = 'Представитель администрации'

    faculties: List[Faculty] = association_proxy('_faculties', 'faculty')

    def appeal(self, case=None):
        if case is not None:
            from Domain.functools.Format import inflect
            return f"{inflect('представитель', case)} администрации {self.full_name(case)}"
        else:
            return f"{self.type_name} {self.full_name()}"

    def __repr__(self):
        return f"<Administration(id={self.id}, card_id={self.email}, " \
            f"last_name={self.last_name}, first_name={self.first_name}, " \
            f"middle_name={self.middle_name})>"

    @classmethod
    @filter_deleted
    @listed
    def of(cls, obj, *args, **kwargs) -> List['Administration']:
        """
        Возвращает список Администраторов, которые относятся к переданому объекту
        :param obj: Объект базы данных
        :return: список
        """
        if isinstance(obj, Professor):
            return Administration.of(Faculty.of(obj))

        if isinstance(obj, Faculty):
            return obj.admins

        raise NotImplementedError(type(obj))


class Professor(Base, _DBPerson, _DBRoot):
    """
    Таблица преподавателей
    """
    __tablename__ = 'professors'
    type_name = 'Преподаватель'

    _last_update_in = Column(DateTime, default=datetime.now)
    _last_update_out = Column(DateTime)

    lessons: List[Lesson] = relationship("Lesson", backref=backref('professor'), order_by="Lesson.date")

    departments: List[Department] = association_proxy('_department', 'department')

    _auth: Auth = None

    def groups(self, with_deleted=False) -> List[List['Group']]:
        return [list(item)
                for item in set(frozenset(g for g in lesson.groups if not g | with_deleted)
                                for lesson in self.lessons)]

    @classmethod
    @filter_deleted
    @filter_semester
    @listed
    def of(cls, obj, *args, **kwargs) -> List['Professor']:
        """

        :param obj: объект или спсиок объектов базы данных
        :return: список преподавателей, отоносящихся к объекту
        """

        if isinstance(obj, Visitation):
            return [lesson.professor for lesson in obj.lesson]

        if isinstance(obj, Student):
            return Professor.of(obj.groups)

        if isinstance(obj, (Group, Discipline, Semester)):
            return Professor.of(obj.lessons)

        if isinstance(obj, Professor):
            return [obj]

        if isinstance(obj, Department):
            return obj.professors

        if isinstance(obj, Lesson):
            return [obj.professor]

        raise NotImplementedError(type(obj))

    def updates(self, last_in: datetime = None) -> Dict[str, Dict[str, List]]:
        """

        :return: кортеж из трех словарей:
            созданные объекты этим преподавтелем с момента последней отправки,
            измененные объекты этим преподавтелем с момента последней отправки,
            удаленные объекты этим преподавтелем с момента последней отправки
        """

        created = {}
        updated = {}
        deleted = {}

        if self._last_update_out is None:
            self._last_update_out = datetime(2008, 1, 1)

        updateable: List[Type[_DBTrackedObject]] = [x for x in _DBTrackedObject.subclasses() if x != Auth]

        for cls in updateable:
            updated[cls.__name__] = self.session() \
                .query(cls) \
                .filter(cls._updated > (self._last_update_out if last_in is None else last_in)) \
                .all()

            created[cls.__name__] = self.session() \
                .query(cls) \
                .filter(cls._created > (self._last_update_out if last_in is None else last_in)) \
                .all()

            deleted[cls.__name__] = self.session() \
                .query(cls) \
                .filter(cls._deleted > (self._last_update_out if last_in is None else last_in)) \
                .all()

        return dict(created=created, updated=updated, deleted=deleted)


class Group(Base, _DBNamedObject, _DBEmailObject, _DBTrackedObject, _DBRoot):
    """
    Таблица групп
    """
    __tablename__ = 'groups'
    type_name = "Группа"

    faculty_id = Column(Integer, ForeignKey('faculties.id'))

    faculty: Faculty

    _students = relationship('StudentsGroups', backref=backref('group'))
    students: List['Student'] = association_proxy('_students', 'student')

    _lessons = relationship('LessonsGroups', backref=backref('group'))
    lessons: List[Lesson] = association_proxy('_lessons', 'lesson')

    def __repr__(self):
        return f"<Group(id={self.id}, name={self.name})>"

    @classmethod
    @filter_deleted
    @filter_semester
    @listed
    def of(cls, obj, *args, **kwargs) -> List['Group'] or List[List['Group']]:
        """

        :param obj: объект или спсиок объектов базы данных
        :return: список групп, отоносящихся к объекту
        """

        if isinstance(obj, Lesson):
            return obj.groups

        if isinstance(obj, (Discipline, Semester, Room, LessonType)):
            return Group.of(obj.lessons)

        if isinstance(obj, Student):
            return obj.groups

        if isinstance(obj, Professor):
            return obj.groups()

        if isinstance(obj, Faculty):
            return obj.groups

        if isinstance(obj, Department):
            return Group.of(Discipline.of(obj))

        if isinstance(obj, Building):
            return Group.of(obj.rooms)

        if isinstance(obj, Group):
            return [obj]

        raise NotImplementedError(type(obj))

    def filter(self, lessons: List['Lesson']):
        return [l for l in lessons if self in Group.of(l)]


class Student(Base, _DBPerson, _DBRoot):
    """
    Таблица студентов
    """
    type_name = 'Студент'

    __tablename__ = 'students'

    _parents = relationship('StudentsParents', backref=backref('student'))
    parents: List['Parent'] = association_proxy('_parents', 'parent')

    _groups = relationship('StudentsGroups', backref=backref('student'))
    groups: List[Group] = association_proxy('_groups', 'group', creator=lambda group: StudentsGroups(group=group))

    visitations: List[Visitation] = relationship("Visitation", backref=backref('student'))

    def __repr__(self):
        return f"<Student(id={self.id}, card_id={self.card_id}," \
            f" last_name={self.last_name}, first_name={self.first_name}, " \
            f"middle_name={self.middle_name})>"

    @classmethod
    @filter_deleted
    @filter_semester
    @sorter
    @listed
    def of(cls, obj, *args, **kwargs) -> List['Student']:
        """

        :param obj: объект или спсиок объектов базы данных
        :return: список студентов, отоносящихся к объекту
        """

        if isinstance(obj, Group):
            return obj.students

        if isinstance(obj, (Faculty, Lesson)):
            return Student.of(obj.groups)

        if isinstance(obj, (Professor, Discipline, Semester, LessonType)):
            return Student.of(obj.lessons)

        if isinstance(obj, Department):
            return Student.of(Discipline.of(obj))

        if isinstance(obj, Student):
            return [obj]

        if isinstance(obj, Room):
            return Student.of(obj.lessons)

        if isinstance(obj, Building):
            return Student.of(obj.rooms)

        raise NotImplementedError(type(obj))


class Parent(Base, _DBPerson):
    """
    Таблица содержащая информациюо родителях
    """
    __tablename__ = "parents"
    type_name = "Родитель"

    _students = relationship("StudentsParents", backref=backref('parent'))
    students: List[Student] = association_proxy('_students', 'student')

    @classmethod
    @listed
    def of(cls, obj, *args, **kwargs) -> List['Parent']:
        """

        :param obj: объект или спсиок объектов базы данных
        :return: список родителей, отоносящихся к объекту
        """

        if isinstance(obj, Student):
            return obj.parents

        if isinstance(obj, Professor):
            return Parent.of(Student.of(obj))

        raise NotImplementedError(type(obj))


Base.metadata.create_all(engine)

