"""
safsdf
"""
from itertools import chain
from typing import List

import sqlalchemy
from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Boolean, func, event
from sqlalchemy import create_engine, Table
from sqlalchemy.ext.associationproxy import association_proxy
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship, backref, scoped_session

# from Client.Domain.Data import students_of_groups
from DataBase.config2 import DataBaseConfig
from DataBase2.Exception import VisitationAlreadyExist

engine = create_engine('sqlite:///{}'.format(DataBaseConfig().db['database']), echo=False)

Base = declarative_base()

Session = scoped_session(sessionmaker(bind=engine))
session = Session()

students_groups = Table('students_groups', Base.metadata,
                        Column('student_id', Integer, ForeignKey('students.id')),
                        Column('group_id', Integer, ForeignKey('groups.id')))

professors_updates = Table('professors_updates', Base.metadata,
                           Column('professor_id', Integer, ForeignKey('professors.id')),
                           Column('update_id', Integer, ForeignKey('updates.id')))

lessons_groups = Table('lessons_groups', Base.metadata,
                       Column('lesson_id', Integer, ForeignKey('lessons.id')),
                       Column('group_id', Integer, ForeignKey('groups.id')))


class UserType(int):
    STUDENT = 0
    PROFESSOR = 2
    PARENT = 1
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
                self._user = session.query(Student).filter(Student.id == self.user_id).first()
            elif self.user_type == 1:
                self._user = session.query(Professor).filter(Professor.id == self.user_id).first()
        return self._user

    @staticmethod
    def log_in(login, password):
        return session.query(Auth).filter(Auth.login == login).filter(Auth.password == password).first()

    def __repr__(self):
        return f"<Auth(id={self.id}, user_type={self.user_type}, user_id={self.user_id})>"


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
        return f"<Discipline(id={self.id}, name={self.name})>"


class Lesson(Base):
    """
    Lesson
    """
    __tablename__ = 'lessons'

    id = Column(Integer, primary_key=True)
    professor_id = Column(Integer, ForeignKey('professors.id'))
    discipline_id = Column(Integer, ForeignKey('disciplines.id'))
    type = Column(Integer)
    _date = Column('date', DateTime)
    _completed = Column('completed', Integer)
    room_id = Column(String)

    groups = relationship("Group", secondary=lessons_groups)

    discipline = relationship("Discipline", lazy='joined')

    visitations = relationship('Visitation')

    professors = relationship('Professor')

    @property
    def completed(self):
        """

        :return: completed status of lesson
        """
        return self._completed

    @completed.setter
    def completed(self, status):
        self._completed = status
        Update.new(self)
        session.commit()

    @property
    def date(self):
        """

        :return: date of lesson
        """
        return self._date

    @date.setter
    def date(self, value):
        self._date = value
        Update.new(self)
        session.commit()

    @staticmethod
    def filter(professor: 'Professor', discipline: Discipline, group: 'Group' or List['Group']):
        """

        :param professor:
        :param discipline:
        :param group:
        :return: lessons of current discipline
        """
        return sorted(list(filter(lambda x: (set(group) == set(x.groups) or (len(group) == 1 and group[0] in x.groups))
                                            and x.discipline == discipline, professor.lessons)),
                      key=lambda x: x.date)

    def __repr__(self):
        return f"<Lesson(id={self.id}, professor_id={self.professor_id}," \
               f" discipline_id={self.discipline_id}, " \
               f"date={self.date}, type={self.type}, completed={self.completed})>"


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
        print('admins after new', session.query(Administration).all(), session.dirty, admin)

    __tablename__ = 'administrations'

    id = Column(Integer, unique=True, autoincrement=True)
    first_name = Column(String, primary_key=True)
    last_name = Column(String, primary_key=True)
    middle_name = Column(String, primary_key=True)
    email = Column(String)

    _professors = None

    @property
    def professors(self):
        """

        :return: all professors contacts of administration
        """
        if self._professors is None:
            self._professors = session \
                .query(Professor) \
                .join(NotificationParam) \
                .filter(NotificationParam.admin_id == self.id) \
                .all()
        return self._professors

    _notification = None

    def notification(self, professor) -> 'NotificationParam':
        if self._notification is None:
            self._notification = session \
                .query(NotificationParam) \
                .filter(NotificationParam.admin_id == self.id) \
                .filter(NotificationParam.professor_id == professor.id) \
                .first()
        return self._notification


class Professor(Base):
    """
    Professor
    """
    __tablename__ = 'professors'

    id = Column(Integer, unique=True, autoincrement=True)
    first_name = Column(String, primary_key=True)
    last_name = Column(String, primary_key=True)
    middle_name = Column(String, primary_key=True)
    _card_id = Column('card_id', String, unique=True)

    lessons: List[Lesson] = relationship("Lesson", backref=backref("professor", order_by="Lesson._date"))

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
            self._disciplines = list(set(map(lambda x: x.discipline, self.lessons)))
        return self._disciplines

    # groups
    _groups = None

    @property
    def groups(self):
        """

        :return: list of groups
        """
        if self._groups is None:
            self._groups = list(map(lambda y: list(y), list(set(map(lambda x: frozenset(x.groups), self.lessons)))))
        return self._groups

    _students = None

    @property
    def students(self):
        if self._students is None:
            self._students = set(chain.from_iterable(map(lambda x: x.students, chain.from_iterable(self.groups))))
        return self._students

    @property
    def card_id(self):
        """
        Need to update card ID
        :return: card ID of student
        """
        return self._card_id

    @card_id.setter
    def card_id(self, value):
        self._card_id = value
        Update.new(self)
        session.commit()

    updates = relationship('Update', secondary=professors_updates)

    def __repr__(self):
        return f"<Professor(id={self.id}, card_id={self.card_id}, last_name={self.last_name}, " \
               f"first_name={self.first_name}, middle_name={self.middle_name})>"


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
        np = NotificationParam(professor_id=professor.id, admin_id=admin.id, active=True, id=ID(NotificationParam))
        session.add(np)
        Update.new(np, Update.ActionType.NEW)
        return np

    __tablename__ = 'notifications'

    id = Column(Integer, primary_key=True)
    professor_id = Column(Integer, ForeignKey('professors.id'))
    admin_id = Column(Integer, ForeignKey('administrations.id'))
    _active = Column('active', Boolean)

    admin = relationship('Administration', lazy='select')

    _professors = None

    @property
    def professors(self) -> List[Professor]:
        if self._professors is None:
            self._professors = session \
                .query(Professor) \
                .join(NotificationParam) \
                .filter(NotificationParam.admin_id == self.admin_id) \
                .all()
        return self._professors

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


class Student(Base):
    """
    Student
    """

    @staticmethod
    def find(card_id):
        return session.query(Student).filter(Student.card_id == card_id).first()

    __tablename__ = 'students'

    id = Column(Integer, ForeignKey('students_parents.student_id'), unique=True, autoincrement=True)
    first_name = Column(String, primary_key=True)
    last_name = Column(String, primary_key=True)
    middle_name = Column(String, primary_key=True)
    _card_id = Column('card_id', String, unique=True)

    _parents = relationship('StudentsParents', back_populates="student", foreign_keys='Student.id')
    parents = association_proxy('_parents', 'parent')

    groups = relationship("Group", secondary=students_groups, lazy='select')

    visitations = relationship("Visitation", backref=backref("student"))

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

    @property
    def card_id(self):
        """

        :return: card ID of student
        """
        return self._card_id

    @card_id.setter
    def card_id(self, value):
        self._card_id = value
        Update.new(self)
        session.commit()

    def __repr__(self):
        return f"<Student(id={self.id}, card_id={self.card_id}, last_name={self.last_name}, " \
               f"first_name={self.first_name}, middle_name={self.middle_name})>"


class Parent(Base):
    @staticmethod
    def new(student, last_name, first_name, middle_name, email, sex, professor=None):
        existing: Parent = session \
            .query(Parent) \
            .filter(Parent.last_name == last_name) \
            .filter(Parent.first_name == first_name) \
            .filter(Parent.middle_name == middle_name).filter(Parent.email == email) \
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
            Update.new(new_object, action_type=Update.ActionType.NEW, performer=professor)

        session.commit()

    __tablename__ = "parents"

    id = Column(Integer, ForeignKey('students_parents.parent_id'), unique=True, autoincrement=True)
    first_name = Column(String, primary_key=True)
    last_name = Column(String, primary_key=True)
    middle_name = Column(String, primary_key=True)
    sex = Column(Integer)
    email = Column(String, primary_key=True)

    _students = relationship("StudentsParents", back_populates="parent", foreign_keys='Parent.id')

    students = association_proxy('_students', 'student')


class StudentsParents(Base):
    __tablename__ = 'students_parents'

    parent_id = Column(Integer, ForeignKey('parents.id'), primary_key=True)
    student_id = Column(Integer, ForeignKey('students.id'), primary_key=True)

    parent = relationship("Parent", foreign_keys='StudentsParents.parent_id')
    student = relationship("Student", foreign_keys='StudentsParents.student_id')


class Group(Base):
    """
    Group
    """
    __tablename__ = 'groups'

    id = Column(Integer, unique=True, autoincrement=True)
    name = Column(String, primary_key=True)

    students = relationship("Student", secondary=students_groups, lazy='select')
    lessons = relationship("Lesson", secondary=lessons_groups, lazy='select')

    def __repr__(self):
        return f"<Group(id={self.id}, name={self.name})>"


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
    def new(updated_object, action_type=ActionType.UPDATE, performer=None):
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

            update.professors.extend(professors_affected)
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
                .filter(Update.table_name == updated_object.__tablename__).filter(
                Update.row_id == updated_object.id).all()

            if len(old_update) == 0:
                return make()

    @staticmethod
    def all(professor=None):
        if professor is not None:
            return session.query(Update).join(Professor).filter(Professor.id == professor.id).all()
        return session.query(Update).all()

    @staticmethod
    def delete(professor=None):
        if professor is not None:
            session.query(Update).join(Professor).filter(Professor.id == professor.id).delete()
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

    professors = relationship("Professor", secondary=professors_updates)

    def __repr__(self):
        return f"<Update(id={self.id}, table_name={self.table_name}, row_id={self.row_id})>"

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


class Visitation(Base):
    """
    Visitation
    """

    __tablename__ = 'visitations'

    id = Column(Integer, unique=True, autoincrement=True)
    student_id = Column(Integer, ForeignKey('students.id', ondelete="RESTRICT"), primary_key=True)
    lesson_id = Column(Integer, ForeignKey('lessons.id', ondelete="RESTRICT"), primary_key=True)

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
    def new(student: Student, lesson: Lesson):
        """
        Creates new visitation and update.
        :param student:
        :param lesson:
        :return:
        """

        def calculate_id():
            """

            :return: ID of visitation in special format
            """
            import time
            value = (lesson.id * pow(10, 6) + student.id) * pow(10, 8) + int(time.time() % (3.154 * pow(10, 7)))
            return value

        row_id = calculate_id()

        visit = Visitation(student_id=student.id, lesson_id=lesson.id, id=row_id)

        try:
            session.add(visit)

            Update.new(visit, Update.ActionType.NEW)

            session.commit()

        except sqlalchemy.orm.exc.FlushError:
            session.rollback()
            raise VisitationAlreadyExist()

        finally:
            return visit

    def delete(self):
        """
        deletes this visitation
        """
        Update.new(self, Update.ActionType.DELETE)
        session.delete(self)
        session.commit()

    def __repr__(self):
        return f'<Visitation(student_id={self.student_id}, lesson_id={self.lesson_id})>'


@event.listens_for(Lesson, "before_delete")
def before_delete(mapper, connect, target):
    print(target, "will be deleted")


if __name__ == '__main__':
    pass
    # auth = session.query(Auth).filter(Auth.login == 'VAE').filter(Auth.password == '123456').first()
#
# professor = auth.user
#
# disciplines = professor.disciplines
#
# print(professor.students)
#
# for discipline in disciplines:
#    print(discipline)
#
#    for groups in professor.groups:
#        print('\t', groups)
#
#        print('\t\t', 'lessons')
#        for lesson in Lesson.filter(professor, discipline, groups):
#            print('\t\t\t', lesson, lesson.groups)
#
#        print('\t\t students')
#        for student in students_of_groups(groups):
#            print('\t\t\t', student)

# for discipline in disciplines:
#     print(discipline)
#
#     for group in set(map(lambda y: y.group, list(filter(lambda x: x.discipline == discipline, professor.lessons)))):
#         print('\t', group)
#
#         for lesson in list(filter(lambda x: x.discipline == discipline and x.group == group, professor.lessons)):
#             print('\t\t', lesson)

# for discipline in disciplines:
#    print(discipline)
#
#    lessons = set(filter(lambda x: x.type == 0, professor.lessons))
#    lessons_s = {l.date: frozenset(map(
#        lambda x: x.group,
#        set(filter(
#            lambda x: x.date == l.date and x.room_id == l.room_id,
#            lessons))))
#        for l in lessons}
#    print(lessons_s)
#    groups_l = set(map(lambda x: lessons_s[x], lessons_s.keys()))
#    for group in groups_l:
#        print('\t', group)
#
#        for lesson in set(filter(lambda x: lessons_s[x] == group, lessons_s.keys())):
#            print('\t\t', lessons)
#
