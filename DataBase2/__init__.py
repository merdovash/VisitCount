"""

safsdf
"""
import os
import sys
from itertools import chain
from typing import List

from sqlalchemy.pool import QueuePool

from DataBase2.config2 import DataBaseConfig
from Exception import NoSuchUserException

try:
    root = sys.modules['__main__'].__file__
    print(sys.modules['__main__'].__file__)
except AttributeError:
    root = "run_client.py"

_new = False

if root == 'run_server.py':
    db_path = os.path.abspath('DataBase2\\server.db')

    from sqlalchemy import create_engine

    engine = create_engine(f"sqlite:///{db_path}")

    from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, \
        Boolean, func, event
    from sqlalchemy.ext.associationproxy import association_proxy
    from sqlalchemy.orm import sessionmaker, relationship, scoped_session

    from sqlalchemy.ext.declarative import declarative_base

    # session = scoped_session(sessionmaker(bind=engine))

    Base = declarative_base(bind=engine)

    Session = scoped_session(sessionmaker(bind=engine))

    metadata = Base.metadata

else:
    import sqlalchemy
    from sqlalchemy.ext.declarative import declarative_base

    Base = declarative_base()

    from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, \
        Boolean, func, event
    from sqlalchemy import create_engine
    from sqlalchemy.ext.associationproxy import association_proxy
    from sqlalchemy.orm import sessionmaker, relationship, scoped_session

    db_path = 'sqlite:///{}'.format(DataBaseConfig().db['database'])

    try:
        fh = open(db_path.split('///')[1], 'r')
        fh.close()
    except FileNotFoundError:
        fh = open(db_path.split('///')[1], 'w+')
        fh.close()
        _new = True

    engine = create_engine(db_path, echo=False, poolclass=QueuePool)

    Session = scoped_session(sessionmaker(bind=engine))
    # session = Session()

    metadata = Base.metadata

# from Client.Domain.Data import students_of_groups
from DataBase2.Exception import VisitationAlreadyExist


class Connection():
    _instance = None

    @staticmethod
    def get():
        if Connection._instance is None:
            Connection._instance = Session()
        return Connection._instance


session = Connection.get()


class StudentsGroups(Base):
    __tablename__ = 'students_groups'
    id = Column(Integer, primary_key=True)
    student_id = Column(Integer, ForeignKey('students.id'), primary_key=True)
    group_id = Column(Integer, ForeignKey('groups.id'), primary_key=True)

    student = relationship('Student')
    group = relationship('Group')


class ProfessorsUpdates(Base):
    __tablename__ = 'professors_updates'
    id = Column(Integer, primary_key=True)
    professor_id = Column(Integer, ForeignKey('professors.id'),
                          primary_key=True)
    update_id = Column(Integer, ForeignKey('updates.id'),
                       primary_key=True)

    professor = relationship('Professor')
    update = relationship('Update')

    def __init__(self, **kwargs):
        self.id = ID(self)
        self.professor_id = kwargs.get('professor_id')
        self.update_id = kwargs.get('update_id')


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

    id = Column(Integer, unique=True, autoincrement=True)
    student_id = Column(Integer,
                        ForeignKey('students.id', ondelete="RESTRICT"),
                        primary_key=True)
    lesson_id = Column(Integer,
                       ForeignKey('lessons.id', ondelete="RESTRICT"),
                       primary_key=True)

    lesson = relationship('Lesson')
    student = relationship('Student')

    _professor = None

    @property
    def professors(self):
        """

        :return: all professors of this visitation
        """
        if self._professor is None:
            self._professor = session.query(Professor) \
                .join(Lesson) \
                .join(Visitation) \
                .filter(Visitation.id == self.id) \
                .all()
        return self._professor

    @staticmethod
    def new(student: 'Student', lesson: 'Lesson'):
        """
        Creates new visitation and update.
        :param student:
        :param lesson:
        :return:
        """

        row_id = ID(Visitation)

        visit = Visitation(student_id=student.id, lesson_id=lesson.id,
                           id=row_id)

        try:
            session.add(visit)

            Update.new(visit, Update.ActionType.NEW)

            session.flush()

            session.commit()

        except sqlalchemy.orm.exc.FlushError:
            session.rollback()
            raise VisitationAlreadyExist()

        finally:
            return visit

    def delete(self, session):
        """
        deletes this visitation
        """

        Update.new(self, session=session,
                   action_type=Update.ActionType.DELETE)
        session.delete(self)
        session.flush()
        session.commit()

    def __repr__(self):
        return f'<Visitation(student_id={self.student_id},' \
               f' lesson_id={self.lesson_id})>'


class UserType(int):
    STUDENT = 0
    PROFESSOR = 1
    PARENT = 2
    ADMIN = 3


def ID(table):
    max_index = session.query(func.max(table.id)).first()[0]
    return max_index + 1 if max_index else 1


class Auth(Base):
    """
    Authentication table
    """
    __tablename__ = 'auth5'

    id = Column(Integer, unique=True, autoincrement=True)
    login = Column(String, primary_key=True, unique=True)
    password = Column(String, primary_key=True)
    uid = Column(String, unique=True)
    user_type = Column(Integer)
    user_id = Column(Integer)

    _user = None

    @property
    def user(self):
        """

        :return: Professor or Student
        """
        if self._user is None:
            if self.user_type == 0:
                self._user = session.query(Student).filter(
                    Student.id == self.user_id).first()
            elif self.user_type == 1:
                self._user = session.query(Professor).filter(
                    Professor.id == self.user_id).first()
        return self._user

    @staticmethod
    def log_in(login, password, session=session) -> 'Auth':
        res = session \
            .query(Auth) \
            .filter(Auth.login == login) \
            .filter(Auth.password == password) \
            .first()

        if res is None:
            raise NoSuchUserException()

        return res

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
    name = Column(String, primary_key=True)

    lessons = relationship('Lesson')

    _groups = None

    @property
    def groups(self):
        """

        :return: group of discipline
        """
        if self._groups is None:
            self._groups = set(map(lambda x: x.groups, self.lessons))
        return self._groups

    def __repr__(self):
        return f"<Discipline(id={self.id}," \
               f" name={self.name})>"


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
    room_id = Column(String)

    _groups = relationship('LessonsGroups')
    groups = association_proxy('_groups', 'group')

    discipline = relationship("Discipline", lazy='joined')

    visitations = relationship('Visitation')

    professors = relationship('Professor')

    @staticmethod
    def filter(professor: 'Professor', discipline: Discipline,
               group: 'Group' or List['Group']):
        """

        :param professor:
        :param discipline:
        :param group:
        :return: lessons of current discipline
        """
        return sorted(list(filter(lambda x: (set(group) == set(x.groups) or (
                len(group) == 1 and group[0] in x.groups))
                                            and x.discipline == discipline,
                                  professor.lessons)),
                      key=lambda x: x.date)

    def __repr__(self):
        return f"<Lesson(id={self.id}, professor_id={self.professor_id}," \
               f" discipline_id={self.discipline_id}, " \
               f"date={self.date}, type={self.type}," \
               f" completed={self.completed})>"


class Administration(Base):
    """
    Administration user
    """

    @staticmethod
    def new(last_name, first_name, middle_name, email, professor):
        admin = Administration(last_name=last_name,
                               first_name=first_name,
                               middle_name=middle_name,
                               email=email,
                               id=ID(Administration))
        session.add(admin)
        NotificationParam.new(professor, admin)
        Update.new(admin, Update.ActionType.NEW)

        session.commit()
        print('admins after new', session.query(Administration).all(),
              session.dirty, admin)

    __tablename__ = 'administrations'

    id = Column(Integer, unique=True, autoincrement=True)
    first_name = Column(String, primary_key=True)
    last_name = Column(String, primary_key=True)
    middle_name = Column(String, primary_key=True)
    email = Column(String)

    notification = relationship('NotificationParam')
    professors = association_proxy('notification', 'professor')


class Professor(Base):
    """
    Professor
    """
    __tablename__ = 'professors'

    id = Column(Integer, unique=True, autoincrement=True)
    first_name = Column(String, primary_key=True)
    last_name = Column(String, primary_key=True)
    middle_name = Column(String, primary_key=True)
    card_id = Column('card_id', String, unique=True)

    lessons: List[Lesson] = relationship("Lesson", order_by="Lesson.date")

    _admins = relationship('NotificationParam')
    admins = association_proxy('_admins', 'admin')

    @property
    def professors(self):
        """
        Need to update function
        :return: self
        """
        return [self]

    # disciplines
    _disciplines = None

    @property
    def disciplines(self):
        """

        :return: list of disciplines
        """
        if self._disciplines is None:
            self._disciplines = list(
                set(map(lambda x: x.discipline, self.lessons)))
        return self._disciplines

    # groups
    _groups = None

    @property
    def groups(self):
        """

        :return: list of groups
        """
        if self._groups is None:
            self._groups = list(map(lambda y: list(y), list(
                set(map(lambda x: frozenset(x.groups), self.lessons)))))
        return self._groups

    _students = None

    @property
    def students(self):
        if self._students is None:
            self._students = set(chain.from_iterable(
                map(lambda x: x.students, chain.from_iterable(self.groups))))
        return self._students

    _updates = relationship('ProfessorsUpdates')
    updates = association_proxy('_updates', 'update')

    def __repr__(self):
        return f"<Professor(id={self.id}, card_id={self.card_id}, " \
               f"last_name={self.last_name}, first_name={self.first_name}, " \
               f"middle_name={self.middle_name})>"


class NotificationParam(Base):
    """
    Notification
    """

    @staticmethod
    def new(professor: Professor, admin: Administration):
        """
        creates new contact from professor and admin
        add new update
        :param professor:
        :param admin:
        :return:
        """
        np = NotificationParam(professor_id=professor.id, admin_id=admin.id,
                               active=True, id=ID(NotificationParam))
        session.add(np)
        Update.new(np, Update.ActionType.NEW)
        return np

    __tablename__ = 'notifications'

    id = Column(Integer, primary_key=True)
    professor_id = Column(Integer, ForeignKey('professors.id'))
    admin_id = Column(Integer, ForeignKey('administrations.id'))
    _active = Column('active', Boolean)

    admin = relationship('Administration', lazy='select')

    professors = relationship('Professor')

    @property
    def active(self):
        """

        :return: active status
        """
        return self._active

    @active.setter
    def active(self, val: bool):
        self._active = val
        Update.new(self, Update.ActionType.UPDATE)
        session.commit()


class Group(Base):
    """
    Group
    """
    __tablename__ = 'groups'

    id = Column(Integer, unique=True, autoincrement=True)
    name = Column(String, primary_key=True)

    _students = relationship('StudentsGroups')
    students = association_proxy('_students', 'student')

    _lessons = relationship('LessonsGroups')
    lessons = association_proxy('_lessons', 'lesson')

    def __repr__(self):
        return f"<Group(id={self.id}, name={self.name})>"


class Student(Base):
    """
    Student
    """

    __tablename__ = 'students'

    id = Column(Integer, unique=True, autoincrement=True)
    first_name = Column(String, primary_key=True)
    last_name = Column(String, primary_key=True)
    middle_name = Column(String, primary_key=True)
    card_id = Column(String)

    _parents = relationship('StudentsParents')
    parents = association_proxy('_parents', 'parent')

    _groups = relationship('StudentsGroups')
    groups = association_proxy('_groups', 'group')

    visitations = relationship("Visitation")

    _professors = None

    @property
    def professors(self):
        """

        :return: professors of student
        """
        if self._professors is None:
            self._professors = session.query(Professor) \
                .join(Lesson) \
                .join(Group) \
                .filter(Group.id.in_(list(map(lambda x: x.id, self.groups)))) \
                .all()
        return self._professors

    def __repr__(self):
        return f"<Student(id={self.id}, card_id={self.card_id}," \
               f" last_name={self.last_name}, first_name={self.first_name}, " \
               f"middle_name={self.middle_name})>"


class Parent(Base):
    @staticmethod
    def new(student, last_name, first_name, middle_name, email, sex,
            professor=None):
        existing: Parent = session \
            .query(Parent) \
            .filter(Parent.last_name == last_name) \
            .filter(Parent.first_name == first_name) \
            .filter(Parent.middle_name == middle_name).filter(
            Parent.email == email) \
            .first()

        if existing is not None:
            existing.students.append(student)
        else:
            new_parent = Parent(last_name=last_name, first_name=first_name,
                                middle_name=middle_name, email=email,
                                id=ID(Parent), sex=sex)

            assosiation = StudentsParents()
            assosiation.student = student
            assosiation.parent = new_parent

            session.add(new_parent)
            session.add(assosiation)

        list_of_new = session.dirty

        print(list_of_new)
        for new_object in session.dirty:
            Update.new(new_object, action_type=Update.ActionType.NEW,
                       performer=professor)

        session.commit()

    __tablename__ = "parents"

    id = Column(Integer, primary_key=True)
    first_name = Column(String)
    last_name = Column(String)
    middle_name = Column(String)
    sex = Column(Integer)
    email = Column(String)

    _students = relationship("StudentsParents")
    students = association_proxy('_students', 'student')


class Update(Base):
    """
    Update
    """

    class ActionType(int):
        """
        Update type
        """
        NEW = 2
        UPDATE = 0
        DELETE = 1

    @staticmethod
    def new(updated_object, session, action_type=ActionType.UPDATE,
            performer=None):
        """
        Creates new update and connects to professors
        :param performer:
        :param updated_object:
        :param action_type:
        :return:
        """

        def make():
            update = Update(id=ID(Update),
                            table_name=updated_object.__tablename__,
                            row_id=updated_object.id,
                            action_type=action_type,
                            performer=performer)

            professors_affected = updated_object.professors
            if isinstance(professors_affected, list):
                if performer in professors_affected:
                    professors_affected.remove(performer)

            elif isinstance(professors_affected, Professor):
                if performer == professors_affected:
                    professors_affected = []
                else:
                    professors_affected = [professors_affected]

            print(update.professors, professors_affected)
            update._professors.extend(
                list(map(lambda x: ProfessorsUpdates(professor_id=x.id,
                                                     update_id=update.id),
                         professors_affected)))
            session.add(update)

            return update

        if action_type == Update.ActionType.DELETE:
            old_create = session.query(Update) \
                .filter(Update.table_name == updated_object.__tablename__) \
                .filter(Update.row_id == updated_object.id) \
                .filter(Update.action_type == Update.ActionType.NEW) \
                .first()

            if old_create is not None:
                session.delete(old_create)
            else:
                return make()
        else:
            old_update = session \
                .query(Update) \
                .filter(
                Update.table_name == updated_object.__tablename__).filter(
                Update.row_id == updated_object.id).all()

            if len(old_update) == 0:
                return make()

    @staticmethod
    def all(professor=None):
        if professor is not None:
            return session.query(Update).join(Professor).filter(
                Professor.id == professor.id).all()
        return session.query(Update).all()

    @staticmethod
    def delete(professor=None):
        if professor is not None:
            session.query(Update).join(Professor).filter(
                Professor.id == professor.id).delete()
        else:
            session.query(Update).delete()

    @staticmethod
    def loads(updates: List[dict]):
        for i in updates:
            update = Update(**i)

            session.commit()

    __tablename__ = 'updates'

    id = Column(Integer, unique=True, autoincrement=True)
    table_name = Column(String, primary_key=True)
    row_id = Column(Integer, primary_key=True)
    action_type = Column(Integer, nullable=False)
    performer = Column(Integer)

    _professors = relationship("ProfessorsUpdates", cascade="all, delete-orphan")
    professors = association_proxy('_professors', 'professor')

    def __init__(self, table_name, row_id, performer,
                 action_type=ActionType.UPDATE, id=None):
        self.id = ID(self) if id is None else id
        self.table_name = table_name
        self.row_id = row_id
        self.action_type = action_type
        self.performer = performer

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


@event.listens_for(Lesson.completed, 'set')
def on_update(target, value, oldvalue, initiator):
    print(f"update action: session:{value}, old_value: {oldvalue} ,"
          f"target: {target}, initiator: {initiator}")

    # Update.new(target, action_type=Update.ActionType.UPDATE,
    #            session=Session())


@event.listens_for(Visitation, 'after_insert')
def on_add(mapper, connection, target):
    print(f"session:{session}, mapper: {mapper}, target: {target}")
    Update.new(target, action_type=Update.ActionType.NEW,
               session=Session())
