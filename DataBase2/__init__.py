"""

safsdf
"""
import os
import sys
from collections import defaultdict
from datetime import datetime
from threading import Lock
from typing import List, Union, Tuple, Dict

from sqlalchemy import create_engine, UniqueConstraint, Column, Integer, String, ForeignKey, \
    DateTime, Boolean, event
from sqlalchemy.ext.associationproxy import association_proxy, _AssociationList
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship, scoped_session, backref
from sqlalchemy.orm.attributes import InstrumentedAttribute
from sqlalchemy.pool import SingletonThreadPool, StaticPool, NullPool

from DataBase2.config2 import Config
from Domain.Date import study_week
from Domain.functools.Decorator import memoize, timeit
from Domain.functools.List import flat, unique

try:
    root = sys.modules['__main__'].__file__
    print(sys.modules['__main__'].__file__)
except AttributeError:
    root = "run_client.py"

print(os.path.basename(root))
root = os.path.basename(root)


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
    if root == 'run_server2.py':
        engine = create_engine(Config.connection_string,
                               pool_pre_ping=True,
                               poolclass=NullPool)

    else:
        db_path = 'sqlite:///{}'.format(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'db2.db'))

        engine = create_engine(db_path,
                               echo=False,
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

    Session = scoped_session(sessionmaker(bind=engine, autoflush=False))

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


class _DBObject:
    id = Column(Integer, primary_key=True, unique=True, autoincrement=True)

    def __repr__(self):
        return "<{type}({fields})>".format(
            type=type(self).__name__,
            fields=', '.join("{name}={value}".format(name=name, value=getattr(self, name))
                             for name in dir(self.__class__)
                             if isinstance(getattr(self.__class__, name), InstrumentedAttribute))
        )


class _DBTrackedObject(_DBObject):
    _created = Column(DateTime, default=datetime.now)
    _updated = Column(DateTime, onupdate=datetime.now)
    _is_deleted = Column(Boolean, default=False)
    _deleted = Column(DateTime)

    def delete(self):
        self._is_deleted = True
        self._deleted = datetime.now()

    def restore(self):
        self._deleted = None
        self._is_deleted = False


class _DBPerson(_DBTrackedObject):
    last_name = Column(String(50), nullable=False)
    first_name = Column(String(50), nullable=False)
    middle_name = Column(String(50), default="")
    sex = Column(Boolean, default=True)
    email = Column(String(200))

    session = None

    @classmethod
    def get_by_id(cls, id):
        user_session = Session()

        user = user_session.query(cls).filter(cls.id == id).first()

        if user is not None:
            return UserSession(user, user_session)
        else:
            raise ValueError('user of {id} not found'.format(id=id))


class StudentsGroups(Base, _DBTrackedObject):
    __tablename__ = 'students_groups'
    student_id = Column(Integer, ForeignKey('students.id'))
    group_id = Column(Integer, ForeignKey('groups.id'))

    UniqueConstraint('student_id', 'group_id', name='students_groups_UK')


class LessonsGroups(Base, _DBTrackedObject):
    __tablename__ = 'lessons_groups'

    lesson_id = Column(Integer, ForeignKey('lessons.id'))
    group_id = Column(Integer, ForeignKey('groups.id'))

    UniqueConstraint('lesson_id', 'group_id', name='lesson_groups_UK')


class StudentsParents(Base, _DBTrackedObject):
    __tablename__ = 'students_parents'

    parent_id = Column(Integer, ForeignKey('parents.id'))
    student_id = Column(Integer, ForeignKey('students.id'))

    UniqueConstraint('parent_id', 'student_id', name='student_parent_UK')


class Visitation(Base, _DBTrackedObject):
    """
    Visitation
    """

    __tablename__ = 'visitations'

    student_id = Column(Integer, ForeignKey('students.id'))
    lesson_id = Column(Integer, ForeignKey('lessons.id'))

    UniqueConstraint('student_id', 'lesson_id', 'visitation_UK')

    def __repr__(self):
        return f'<Visitation(id={self.id}, student_id={self.student_id},' \
            f' lesson_id={self.lesson_id})>'

    @staticmethod
    def of(obj):
        if isinstance(obj, (list, _AssociationList)):
            return unique(flat([Visitation.of(o) for o in obj]))
        elif isinstance(obj, (Student, Lesson)):
            return obj.visitations
        elif isinstance(obj, Group):
            return flat(Visitation.of(Student.of(obj)))
        elif isinstance(obj, (Professor, Discipline)):
            return Visitation.of(Lesson.of(obj))
        else:
            raise NotImplementedError(type(obj))


class UserType(int):
    STUDENT = 0
    PROFESSOR = 1
    PARENT = 2
    ADMIN = 3


class Auth(Base, _DBTrackedObject):
    """
    Authentication table
    """
    __tablename__ = 'auth5'

    login = Column(String(40), unique=True)
    password = Column(String(40))
    uid = Column(String(40), unique=True)
    user_type = Column(Integer)
    user_id = Column(Integer)

    _user = None

    @property
    def user(self) -> Union['Student', 'Professor']:
        """

        :return: Professor or Student
        """
        session = Session()
        if self._user is None:
            if self.user_type == 0:
                self._user = session.query(Student).filter(
                    Student.id == self.user_id).first()
            elif self.user_type == 1:
                self._user = session.query(Professor).filter(
                    Professor.id == self.user_id).first()

        return self._user

    def __repr__(self):
        return f"<Auth(id={self.id}," \
            f" user_type={self.user_type}," \
            f" user_id={self.user_id})>"


class Discipline(Base, _DBTrackedObject):
    """
    Discipline
    """
    __tablename__ = 'disciplines'

    name = Column(String(40), nullable=False)
    full_name = Column(String(200))

    lessons = relationship('Lesson', backref=backref('discipline'))

    def __repr__(self):
        return f"<Discipline(id={self.id}," \
            f" name={self.name})>"

    @staticmethod
    def of(obj) -> List['Discipline']:
        if isinstance(obj, Lesson):
            return [obj.discipline]
        elif isinstance(obj, Professor):
            return unique(flat([lesson.discipline for lesson in obj.lessons]))
        else:
            raise NotImplementedError(type(obj))


class Lesson(Base, _DBTrackedObject):
    """
    Lesson
    """
    __tablename__ = 'lessons'

    professor_id = Column(Integer, ForeignKey('professors.id'), nullable=False)
    discipline_id = Column(Integer, ForeignKey('disciplines.id'), nullable=False)
    type = Column(Integer, nullable=False)
    date = Column(DateTime, nullable=False)
    completed = Column(Integer, nullable=False)
    room_id = Column(String(40), nullable=False)

    _groups = relationship('LessonsGroups', backref=backref('lesson'))
    groups = association_proxy('_groups', 'group')

    visitations = relationship('Visitation', backref=backref('lesson'))

    def __repr__(self):
        return f"<Lesson(id={self.id}, professor_id={self.professor_id}," \
            f" discipline_id={self.discipline_id}, " \
            f"date={self.date}, type={self.type}," \
            f" completed={self.completed})>"

    @property
    def week(self):
        return study_week(self.date)

    @staticmethod
    def of(obj, intersect=False) -> List['Lesson']:
        if isinstance(obj, (list, _AssociationList)):
            if intersect:
                lessons = None
                for o in obj:
                    lessons = Lesson.of(o) if lessons is None else list(set(lessons).intersection(Lesson.of(o)))
                return lessons
            else:
                return unique(flat([Lesson.of(o) for o in obj]))
        elif isinstance(obj, (Professor, Discipline, Group)):
            return obj.lessons
        elif isinstance(obj, Student):
            return Lesson.of(obj.groups)
        else:
            raise NotImplementedError(type(obj))


class Administration(Base, _DBPerson):
    """
    Administration user
    """
    __tablename__ = 'administrations'

    notification = relationship('NotificationParam', backref=backref("admin", cascade="all,delete"),
                                passive_updates=False)
    professors = association_proxy('notification', 'professor')

    def __repr__(self):
        return f"<Administration(id={self.id}, card_id={self.email}, " \
            f"last_name={self.last_name}, first_name={self.first_name}, " \
            f"middle_name={self.middle_name})>"

    @staticmethod
    def of(obj) -> List['Administration']:
        if isinstance(obj, (list, _AssociationList)):
            return flat([Administration.of(o) for o in obj])
        elif isinstance(obj, Professor):
            return obj.admins
        elif isinstance(obj, NotificationParam):
            return obj.admin
        else:
            raise NotImplementedError(type(obj))

    @staticmethod
    def active_of(obj):
        if isinstance(obj, Professor):
            nps = list(filter(lambda np: np.active, NotificationParam.of(obj)))
            return Administration.of(nps)
        else:
            raise NotImplementedError(type(obj))


class Professor(_DBPerson, Base):
    """
    Professor
    """
    __tablename__ = 'professors'

    card_id = Column('card_id', String(40), unique=True)

    _last_update_in = Column(DateTime)
    _last_update_out = Column(DateTime)

    lessons: List[Lesson] = relationship("Lesson", backref=backref('professor'), order_by="Lesson.date")

    _admins = relationship('NotificationParam', backref="professor")
    admins = association_proxy('_admins', 'admin')

    session: Session = None

    @staticmethod
    @memoize
    def of(obj) -> List['Professor']:
        if isinstance(obj, (list, _AssociationList, set)):
            return unique(flat([Professor.of(o) for o in obj]))
        elif isinstance(obj, (Lesson, NotificationParam)):
            return [obj.professor]
        elif isinstance(obj, Visitation):
            return Professor.of(obj.lesson)
        elif isinstance(obj, Administration):
            return obj.professors
        elif isinstance(obj, Student):
            return Professor.of(obj.groups)
        elif isinstance(obj, Group):
            return Professor.of(obj.lessons)
        else:
            raise NotImplementedError(type(obj))

    @staticmethod
    def get(professor_id):
        ps = UserSession(professor_id)

        professor = ps.query(Professor).filter(Professor.id == professor_id).first()
        if professor is not None:
            professor.session = ps
        else:
            raise ValueError('professor not found')

    def updates(self)->Tuple[Dict[str, List], Dict[str, List], Dict[str, List]]:
        created = defaultdict(list)
        updated = defaultdict(list)
        deleted = defaultdict(list)

        if self._last_update_out is None:
            self._last_update_out = datetime(2008, 1, 1)

        for class_ in _DBTrackedObject.__subclasses__():
            created[class_.__name__].extend(self.session
                                            .query(class_)
                                            .filter(class_._created >= self._last_update_out)
                                            .filter(class_._is_deleted == False)
                                            .all())
            updated[class_.__name__].extend(self.session
                                            .query(class_)
                                            .filter(class_._updated >= self._last_update_out)
                                            .filter(class_._created < self._last_update_out)
                                            .all())
            deleted[class_.__name__].extend(self.session
                                            .query(class_)
                                            .filter(class_._is_deleted == True)
                                            .filter(class_._deleted >= self._last_update_out)
                                            .all())

        return created, updated, deleted


class NotificationParam(Base, _DBTrackedObject):
    """
    Notification
    """

    __tablename__ = 'notifications'

    professor_id = Column(Integer, ForeignKey('professors.id'))
    admin_id = Column(Integer, ForeignKey('administrations.id'))
    active = Column(Boolean)

    UniqueConstraint('professor_id', 'admin_id', name='notification_param_UK')

    @staticmethod
    def of(obj) -> List['NotificationParam']:
        if isinstance(obj, (list, _AssociationList)):
            return flat([NotificationParam.of(o) for o in obj])
        elif isinstance(obj, Professor):
            return obj._admins
        elif isinstance(obj, Administration):
            return obj.notification
        else:
            raise NotImplementedError(type(obj))

    def __repr__(self):
        return f"<NotificationParam (id={self.id}, professor_id={self.professor_id}, admin_id={self.admin_id}, " \
            f"active={self.active})>"


class Group(Base, _DBTrackedObject):
    """
    Group
    """
    __tablename__ = 'groups'

    name = Column(String(40))

    _students = relationship('StudentsGroups', backref=backref('group'))
    students = association_proxy('_students', 'student')

    _lessons = relationship('LessonsGroups', backref=backref('group'))
    lessons = association_proxy('_lessons', 'lesson')

    def __repr__(self):
        return f"<Group(id={self.id}, name={self.name})>"

    @staticmethod
    def of(obj, flat_list=False) -> List['Group']:
        if isinstance(obj, Lesson):
            return flat(obj.groups) if flat_list else obj.groups
        elif isinstance(obj, Professor):
            if flat_list:
                return unique(flat([lesson.groups for lesson in obj.lessons]))
            else:
                return unique([lesson.groups for lesson in obj.lessons])
        elif isinstance(obj, Discipline):
            if flat_list:
                raise NotImplementedError(f'{type(obj)}, flat_list=True')
            else:
                return unique([Group.of(lesson) for lesson in obj.lessons])
        elif isinstance(obj, Student):
            return obj.groups
        else:
            raise NotImplementedError(type(obj))


class Student(Base, _DBPerson):
    """
    Student
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

    @staticmethod
    def of(obj) -> List['Student']:
        if isinstance(obj, (list, _AssociationList)):
            return flat([Student.of(o) for o in unique(obj)])
        elif isinstance(obj, Group):
            return sorted(obj.students, key=lambda student: student.last_name)
        elif isinstance(obj, Lesson):
            return unique(flat(map(lambda group: Student.of(group), obj.groups)))
        elif isinstance(obj, (Professor, Discipline)):
            return unique(flat(map(lambda lesson: Student.of(lesson.groups), obj.lessons)))
        else:
            raise NotImplementedError(type(obj))


class Parent(Base, _DBPerson):
    __tablename__ = "parents"

    sex = Column(Integer)
    email = Column(String(100))

    _students = relationship("StudentsParents", backref=backref('parent'))
    students = association_proxy('_students', 'student')

    @staticmethod
    def of(obj) -> List['Parent']:
        if isinstance(obj, (list, _AssociationList)):
            return unique(flat([Parent.of(o) for o in obj]))
        elif isinstance(obj, Student):
            return obj.parents
        elif isinstance(obj, Professor):
            return unique(flat(Parent.of(Student.of(obj))))
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
    sess = Session()
    print(type(Professor._admins))
    prof = Professor(last_name="Иванво", first_name="Иван")

    sess.add(prof)

    sess.commit()

    prof.middle_name = "Георг"

    sess.commit()

    print(prof)

    pass
