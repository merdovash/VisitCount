"""

safsdf
"""
import os
import sys
from typing import List

from sqlalchemy import create_engine, UniqueConstraint, Column, Integer, String, ForeignKey, \
    DateTime, Boolean
from sqlalchemy.ext.associationproxy import association_proxy, _AssociationList
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship, scoped_session
from sqlalchemy.pool import SingletonThreadPool

from DataBase2.config2 import DataBaseConfig
from Domain.functools.List import flat, unique, intersect

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
    if root == 'run_server.py':
        engine = create_engine(f"mysql://root:|Oe23zk45|@localhost/bisitor?charset=utf8")

    else:
        db_path = 'sqlite:///{}'.format(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'db.db'))

        engine = create_engine(db_path, echo=False, poolclass=SingletonThreadPool)

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


def ProfessorSession(professor_id, session):
    if session is None:
        s = Session()
    else:
        s = session
    setattr(s, 'professor_id', professor_id)
    return s


class StudentsGroups(Base):
    __tablename__ = 'students_groups'
    id = Column(Integer, primary_key=True)
    student_id = Column(Integer, ForeignKey('students.id'))
    group_id = Column(Integer, ForeignKey('groups.id'))

    UniqueConstraint('student_id', 'group_id', name='students_groups_UK')

    student = relationship('Student')
    group = relationship('Group')


class ProfessorsUpdates(Base):
    __tablename__ = 'professors_updates'
    id = Column(Integer, primary_key=True)
    professor_id = Column(Integer, ForeignKey('professors.id'))
    update_id = Column(Integer, ForeignKey('updates.id'))

    UniqueConstraint('professor_id', 'update_id', name='professor_update_UK')

    professor = relationship('Professor')
    update = relationship('Update')


class LessonsGroups(Base):
    __tablename__ = 'lessons_groups'
    id = Column(Integer, primary_key=True)
    lesson_id = Column(Integer, ForeignKey('lessons.id'))
    group_id = Column(Integer, ForeignKey('groups.id'))

    lesson = relationship('Lesson')
    group = relationship('Group')


class StudentsParents(Base):
    __tablename__ = 'students_parents'

    parent_id = Column(Integer, ForeignKey('parents.id'), primary_key=True)
    student_id = Column(Integer, ForeignKey('students.id'), primary_key=True)

    parent = relationship("Parent")
    student = relationship("Student")


class Visitation(Base):
    """
    Visitation
    """

    __tablename__ = 'visitations'

    id = Column(Integer, primary_key=True, unique=True, autoincrement=True)
    student_id = Column(Integer, ForeignKey('students.id', ondelete="RESTRICT"))
    lesson_id = Column(Integer, ForeignKey('lessons.id', ondelete="RESTRICT"))

    UniqueConstraint('student_id', 'lesson_id', 'visitation_UK')

    lesson = relationship('Lesson')
    student = relationship('Student')

    professors = association_proxy('lesson', 'professor')

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
        else:
            raise NotImplementedError(type(obj))


class UserType(int):
    STUDENT = 0
    PROFESSOR = 1
    PARENT = 2
    ADMIN = 3


class Auth(Base):
    """
    Authentication table
    """
    __tablename__ = 'auth5'

    id = Column(Integer, primary_key=True, unique=True, autoincrement=True)
    login = Column(String(40), unique=True)
    password = Column(String(40))
    uid = Column(String(40), unique=True)
    user_type = Column(Integer)
    user_id = Column(Integer)

    _user = None

    @property
    def user(self):
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


class Discipline(Base):
    """
    Discipline
    """
    __tablename__ = 'disciplines'

    id = Column(Integer, unique=True, autoincrement=True)
    name = Column(String(40), primary_key=True)

    lessons = relationship('Lesson')

    def __repr__(self):
        return f"<Discipline(id={self.id}," \
               f" name={self.name})>"

    @staticmethod
    def of(obj) -> list:
        if isinstance(obj, Lesson):
            return [obj.discipline]
        elif isinstance(obj, Professor):
            return unique(flat([lesson.discipline for lesson in obj.lessons]))
        else:
            raise NotImplementedError(type(obj))


class Lesson(Base):
    """
    Lesson
    """
    __tablename__ = 'lessons'

    id = Column(Integer, primary_key=True)
    professor_id = Column(Integer, ForeignKey('professors.id'))
    discipline_id = Column(Integer, ForeignKey('disciplines.id'))
    type = Column(Integer)
    date = Column(DateTime)
    completed = Column(Integer)
    room_id = Column(String(40))

    _groups = relationship('LessonsGroups')
    groups = association_proxy('_groups', 'group')

    discipline = relationship("Discipline", lazy='joined')

    visitations = relationship('Visitation')

    professor = relationship('Professor')

    def __repr__(self):
        return f"<Lesson(id={self.id}, professor_id={self.professor_id}," \
               f" discipline_id={self.discipline_id}, " \
               f"date={self.date}, type={self.type}," \
               f" completed={self.completed})>"

    @staticmethod
    def of(obj):
        if isinstance(obj, list):
            if isinstance(obj[0], Group):
                return intersect([Lesson.of(o) for o in obj])
            else:
                return unique(flat([Lesson.of(o) for o in obj]))
        elif isinstance(obj, (Professor, Discipline, Group)):
            return obj.lessons
        else:
            raise NotImplementedError(type(obj))


class Administration(Base):
    """
    Administration user
    """
    __tablename__ = 'administrations'

    id = Column(Integer, primary_key=True, unique=True, autoincrement=True)
    first_name = Column(String(40))
    last_name = Column(String(40))
    middle_name = Column(String(40))
    email = Column(String(40))

    notification = relationship('NotificationParam')
    professors = association_proxy('notification', 'professor')

    def __repr__(self):
        return f"<Administration(id={self.id}, card_id={self.email}, " \
               f"last_name={self.last_name}, first_name={self.first_name}, " \
               f"middle_name={self.middle_name})>"

    @staticmethod
    def of(obj):
        if isinstance(obj, (list, _AssociationList)):
            return flat([Administration.of(o) for o in obj])
        elif isinstance(obj, Professor):
            return obj.admins
        else:
            raise NotImplementedError(type(obj))


class Professor(Base):
    """
    Professor
    """
    __tablename__ = 'professors'

    id = Column(Integer, primary_key=True, unique=True, autoincrement=True)
    first_name = Column(String(40))
    last_name = Column(String(40))
    middle_name = Column(String(40))
    card_id = Column('card_id', String(40), unique=True)

    lessons: List[Lesson] = relationship("Lesson", order_by="Lesson.date")

    _admins = relationship('NotificationParam')
    admins = association_proxy('_admins', 'admin')

    # disciplines
    _disciplines = None

    _updates = relationship('ProfessorsUpdates')
    updates = association_proxy('_updates', 'update')

    def __repr__(self):
        return f"<Professor(id={self.id}, card_id={self.card_id}, " \
               f"last_name={self.last_name}, first_name={self.first_name}, " \
               f"middle_name={self.middle_name})>"

    @staticmethod
    def of(obj) -> list:
        if isinstance(obj, list):
            return flat([Professor.of(o) for o in obj])
        elif isinstance(obj, (Lesson, NotificationParam)):
            return [obj.professor]
        elif isinstance(obj, Visitation):
            return Professor.of(obj.lesson)
        elif isinstance(obj, Administration):
            return obj.professors
        else:
            raise NotImplementedError(type(obj))


class NotificationParam(Base):
    """
    Notification
    """

    __tablename__ = 'notifications'

    id = Column(Integer, primary_key=True)
    professor_id = Column(Integer, ForeignKey('professors.id'))
    admin_id = Column(Integer, ForeignKey('administrations.id'))
    active = Column(Boolean)

    UniqueConstraint('professor_id', 'admin_id', name='notification_param_UK')

    admin = relationship('Administration', lazy='select')

    professor = relationship('Professor')

    @staticmethod
    def of(obj):
        if isinstance(obj, (list, _AssociationList)):
            return flat([NotificationParam.of(o) for o in obj])
        elif isinstance(obj, Professor):
            return obj._admins
        else:
            raise NotImplementedError(type(obj))


class Group(Base):
    """
    Group
    """
    __tablename__ = 'groups'

    id = Column(Integer, unique=True, autoincrement=True)
    name = Column(String(40), primary_key=True)

    _students = relationship('StudentsGroups')
    students = association_proxy('_students', 'student')

    _lessons = relationship('LessonsGroups')
    lessons = association_proxy('_lessons', 'lesson')

    def __repr__(self):
        return f"<Group(id={self.id}, name={self.name})>"

    @staticmethod
    def of(obj, flat_list=False) -> list:
        if isinstance(obj, Lesson):
            return flat(obj.groups) if flat_list else obj.groups
        elif isinstance(obj, Professor):
            if flat_list:
                return flat(unique([lesson.groups for lesson in obj.lessons]))
            else:
                return unique([lesson.groups for lesson in obj.lessons])
        elif isinstance(obj, Discipline):
            if flat_list:
                raise NotImplementedError(f'{type(obj)}, flat_list=True')
            else:
                return unique([Group.of(lesson) for lesson in obj.lessons])
        else:
            raise NotImplementedError(type(obj))


class Student(Base):
    """
    Student
    """

    __tablename__ = 'students'

    id = Column(Integer, unique=True, autoincrement=True)
    first_name = Column(String(40), primary_key=True)
    last_name = Column(String(40), primary_key=True)
    middle_name = Column(String(40), primary_key=True)
    card_id = Column(String(40))

    _parents = relationship('StudentsParents')
    parents = association_proxy('_parents', 'parent')

    _groups = relationship('StudentsGroups')
    groups = association_proxy('_groups', 'group')

    visitations = relationship("Visitation")

    _professors = None

    def __repr__(self):
        return f"<Student(id={self.id}, card_id={self.card_id}," \
               f" last_name={self.last_name}, first_name={self.first_name}, " \
               f"middle_name={self.middle_name})>"

    @staticmethod
    def of(obj) -> List['Student']:
        if isinstance(obj, list):
            return flat([Student.of(o) for o in unique(obj)])
        elif isinstance(obj, Group):
            return sorted(obj.students, key=lambda student: student.last_name)
        elif isinstance(obj, Lesson):
            return flat(map(lambda group: Student.of(group), obj.groups))
        elif isinstance(obj, Professor):
            return flat(map(lambda lesson: Student.of(lesson), obj.lessons))
        else:
            raise NotImplementedError(type(obj))


class Parent(Base):
    __tablename__ = "parents"

    id = Column(Integer, primary_key=True)
    first_name = Column(String(40))
    last_name = Column(String(40))
    middle_name = Column(String(40))
    sex = Column(Integer)
    email = Column(String(100))

    _students = relationship("StudentsParents")
    students = association_proxy('_students', 'student')

    @staticmethod
    def of(obj):
        if isinstance(obj, (list, _AssociationList)):
            return unique(flat([Parent.of(o) for o in obj]))
        elif isinstance(obj, Student):
            return obj.parents
        elif isinstance(obj, Professor):
            return unique(flat(Parent.of(Student.of(obj))))
        else:
            raise NotImplementedError(type(obj))


class UpdateType(int):
    """
    Update type
    """
    NEW = 2
    UPDATE = 0
    DELETE = 1


class Update(Base):
    """
    Update
    """

    __tablename__ = 'updates'

    id = Column(Integer, primary_key=True, unique=True, autoincrement=True)
    table_name = Column(String(40))
    row_id = Column(Integer)
    action_type = Column(Integer, nullable=False)
    performer = Column(Integer)

    UniqueConstraint('row_id', 'table_name', name='update_UK')

    _professors = relationship("ProfessorsUpdates", cascade="all, delete-orphan")
    professors = association_proxy('_professors', 'professor')

    def __repr__(self):
        return f"<Update(id={self.id}, table_name={self.table_name}, " \
               f"row_id={self.row_id})>"

    def to_json(self):
        return str(
            {
                'id': self.id,
                'table_name': self.table_name,
                'row_id': self.row_id,
                'action_type': self.action_type,
                'performer': self.performer
            }
        )


if _new:
    Base.metadata.create_all(engine)


# def on_update(target, initiator):
#     print(f"target: {target}, initiator: {initiator}")
#     inner_session = Session()
#     Update.new(target, action_type=Update.ActionType.UPDATE,
#                session=inner_session)
#     inner_session.flush()
#     inner_session.commit()
#
#
# event.listens_for(Student.card_id, 'modified', on_update)
# event.listens_for(Lesson.date, 'modified', on_update)
# event.listens_for(Lesson.completed, 'modified', on_update)
# event.listens_for(Professor.card_id, 'modified', on_update)


# @event.listens_for(Lesson.completed, 'set')
# @event.listens_for(Lesson.date, 'set')
# @event.listens_for(Student.card_id, 'set')
# def on_update(target: Union[Lesson, Student], value, oldvalue, initiator):
#    print(f"update action: value:{value}, old_value: {oldvalue} ,"
#          f"target: {target}, initiator: {initiator}")
#
#    Update.new(target,
#               action_type=Update.ActionType.UPDATE,
#               session=Session.object_session(target),
#               performer=getattr(Session.object_session(target), 'professor_id', None))
#
#
# @event.listens_for(Visitation, 'before_insert')
# def on_add(mapper, session, target):
#    print(f"session:{session}, mapper: {mapper}, target: {target}")
#    Update.new(target, action_type=Update.ActionType.NEW,
#               session=Session())
#
