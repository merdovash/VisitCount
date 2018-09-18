"""
safsdf
"""
from typing import List

import sqlalchemy
from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Boolean, func
from sqlalchemy import create_engine, Table
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship, backref

from DataBase.config2 import DataBaseConfig
from DataBase2.Exception import VisitationAlreadyExist

engine = create_engine('sqlite:///{}'.format(DataBaseConfig().db['database']), echo=False)

Base = declarative_base()

students_groups = Table('students_groups', Base.metadata,
                        Column('student_id', Integer, ForeignKey('students.id')),
                        Column('group_id', Integer, ForeignKey('groups.id')))

professors_updates = Table('professors_updates', Base.metadata,
                           Column('professor_id', Integer, ForeignKey('professors.id')),
                           Column('update_id', Integer, ForeignKey('updates.id')))

lessons_groups = Table('lessons_groups', Base.metadata,
                       Column('lesson_id', Integer, ForeignKey('lessons.id')),
                       Column('group_id', Integer, ForeignKey('groups.id')))


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
    def group(self):
        """

        :return: group of discipline
        """
        if self._groups is None:
            self._groups = set(map(lambda x: x.group, self.lessons))
        return self._groups

    def __repr__(self):
        return f"<Discipline(id={self.id}, name={self.name})>"


class Lesson(Base):
    """
    Lesson
    """
    __tablename__ = 'lessons'

    id = Column(Integer, unique=True, autoincrement=True)

    professor_id = Column(Integer, ForeignKey('professors.id'), primary_key=True)
    # professor = relationship("Professor")

    groups = relationship("Group", secondary=lessons_groups)

    discipline_id = Column(Integer, ForeignKey('disciplines.id'), primary_key=True)
    discipline = relationship("Discipline", lazy='joined')

    type = Column(Integer)
    _date = Column('date', DateTime, primary_key=True)
    _completed = Column('completed', Integer)
    room_id = Column(String)

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
    def filter(professor: 'Professor', discipline: Discipline, group: 'Group'):
        """

        :param professor:
        :param discipline:
        :param group:
        :return: lessons of current discipline
        """
        return sorted(list(filter(lambda x: (set(group) == set(x.groups) or (len(group) == 1 and group[0] in x.groups))
                                            and x.discipline == discipline, professor.lessons)), key=lambda x: x.date)

    def __repr__(self):
        return f"<Lesson(id={self.id}, professor_id={self.professor_id}," \
               f" discipline_id={self.discipline_id}, " \
               f"date={self.date}, type={self.type}, completed={self.completed})>"


class Administration(Base):
    """
    Administration user
    """

    def __init__(self, last_name, first_name, middle_name, email):
        super().__init__(last_name=last_name,
                         first_name=first_name,
                         middle_name=middle_name,
                         email=email)
        Update.new(self, Update.ActionType.NEW)

    __tablename__ = 'administrations'

    id = Column(Integer, unique=True, autoincrement=True)
    first_name = Column(String, primary_key=True)
    last_name = Column(String, primary_key=True)
    middle_name = Column(String, primary_key=True)
    email = Column(String)

    _professors = None

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

    admins = relationship('NotificationParam')

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
        np = NotificationParam(professor.id, admin.id)
        Update.new(np, Update.ActionType.NEW)
        return np

    __tablename__ = 'notifications'

    id = Column(Integer, primary_key=True)
    professor_id = Column(Integer, ForeignKey('professors.id'))
    admin_id = Column(Integer, ForeignKey('administrations.id'))
    _active = Column('active', Boolean)

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


class Student(Base):
    """
    Student
    """
    __tablename__ = 'students'

    id = Column(Integer, unique=True, autoincrement=True)
    first_name = Column(String, primary_key=True)
    last_name = Column(String, primary_key=True)
    middle_name = Column(String, primary_key=True)
    _card_id = Column('card_id', String, unique=True)

    _professors = None

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

    groups = relationship("Group", secondary=students_groups, lazy='select')

    visitations = relationship("Visitation", lazy='joined')

    def __repr__(self):
        return f"<Student(id={self.id}, card_id={self.card_id}, last_name={self.last_name}, " \
               f"first_name={self.first_name}, middle_name={self.middle_name})>"


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

    __tablename__ = 'updates'

    id = Column(Integer, unique=True, autoincrement=True)
    table_name = Column(String, primary_key=True)
    row_id = Column(Integer, primary_key=True)
    action_type = Column(Integer, nullable=False)

    professors = relationship("Professor", secondary=professors_updates)

    def __repr__(self):
        return f"<Update(id={self.id}, table_name={self.table_name}, row_id={self.row_id})>"

    @staticmethod
    def new(updated_object, action_type=ActionType.UPDATE):
        """
        Creates new update and connects to professors
        :param updated_object:
        :param action_type:
        :return:
        """

        def index():
            """

            :return: ID of new row
            """
            max_index = session.query(func.max(Update.id)).first()[0]
            return max_index + 1 if max_index else 0

        update = Update(id=index(),
                        table_name=updated_object.__tablename__,
                        row_id=updated_object.id,
                        action_type=action_type)

        update.professors.extends(updated_object.professors())
        session.add(update)

        return update


class Visitation(Base):
    """
    Visitation
    """
    __tablename__ = 'visitations'

    id = Column(Integer, unique=True, autoincrement=True)
    student_id = Column(Integer, ForeignKey('students.id'), primary_key=True)
    lesson_id = Column(Integer, ForeignKey('lessons.id'), primary_key=True)

    lesson = relationship("Lesson", lazy='joined')
    student = relationship("Student", lazy='select')

    _professor = None

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

    def delete(self):
        """
        deletes this visitation
        """
        self._create_update(Update.ActionType.DELETE)
        session.delete(self)
        session.commit()

    def __repr__(self):
        return f'<Visitation(student_id={self.student_id}, lesson_id={self.lesson_id})>'


Session = sessionmaker(bind=engine)
session = Session()

if __name__ == '__main__':
    auth = session.query(Auth).filter(Auth.login == 'VAE').filter(Auth.password == '123456').first()

    professor = auth.user

    disciplines = professor.disciplines

    for discipline in disciplines:
        print(discipline)

        for group in professor.groups:
            print('\t', group)

            for lesson in Lesson.filter(professor, discipline, group):
                print('\t\t', lesson, lesson.groups)

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
