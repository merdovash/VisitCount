from typing import List

import sqlalchemy
from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, func
from sqlalchemy import create_engine, Table
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship

from DataBase2.Exception import VisitationAlreadyExist

engine = create_engine('sqlite:///db.db', echo=False)

Base = declarative_base()

students_groups = Table('students_groups', Base.metadata,
                        Column('student_id', Integer, ForeignKey('students.id')),
                        Column('group_id', Integer, ForeignKey('groups.id')))

professors_updates = Table('professors_updates', Base.metadata,
                           Column('professor_id', Integer, ForeignKey('professors.id')),
                           Column('update_id', Integer, ForeignKey('updates.id')))


class Auth(Base):
    __tablename__ = 'auth5'

    id = Column(Integer, unique=True, autoincrement=True)
    login = Column(String, primary_key=True, unique=True)
    password = Column(String, primary_key=True)
    user_type = Column(Integer)
    user_id = Column(Integer)

    _user = None

    @property
    def user(self):
        if self._user is None:
            if self.user_type == 0:
                self._user = session.query(Student).filter(Student.id == self.user_id).first()
            elif self.user_type == 1:
                self._user = session.query(Professor).filter(Professor.id == self.user_id).first()
        return self._user

    def __repr__(self):
        return f"<Auth(id={self.id}, user_type={self.user_type}, user_id={self.user_id})>"


class Discipline(Base):
    __tablename__ = 'disciplines'

    id = Column(Integer, unique=True, autoincrement=True)
    name = Column(String, primary_key=True)

    lessons = relationship('Lesson')

    _groups = None

    @property
    def group(self):
        if self._groups is None:
            self._groups = set(map(lambda x: x.group, self.lessons))
        return self._groups

    def __repr__(self):
        return f"<Discipline(id={self.id}, name={self.name})>"


class Lesson(Base):
    __tablename__ = 'lessons'

    id = Column(Integer, unique=True, autoincrement=True)

    professor_id = Column(Integer, ForeignKey('professors.id'), primary_key=True)
    professor = relationship("Professor")

    group_id = Column(Integer, ForeignKey('groups.id'), primary_key=True)
    group = relationship("Group", lazy='joined')

    discipline_id = Column(Integer, ForeignKey('disciplines.id'), primary_key=True)
    discipline = relationship("Discipline", lazy='joined')

    type = Column(Integer)
    _date = Column('date', DateTime, primary_key=True)
    _completed = Column('completed', Integer)
    room_id = Column(String)

    visitations = relationship('Visitation')

    @property
    def completed(self):
        return self._completed

    @completed.setter
    def completed(self, status):
        self._completed = status
        Update.new(self)
        session.commit()

    @property
    def date(self):
        return self._date

    @date.setter
    def date(self, value):
        self._date = value
        Update.new(self)
        session.commit()

    def __repr__(self):
        return f"<Lesson(id={self.id}, professor_id={self.professor_id}," \
               f" group_id={self.group_id}, discipline_id={self.discipline_id}, " \
               f"date={self.date}, type={self.type}, completed={self.completed})>"


class Student(Base):
    __tablename__ = 'students'

    id = Column(Integer, unique=True, autoincrement=True)
    first_name = Column(String, primary_key=True)
    last_name = Column(String, primary_key=True)
    middle_name = Column(String, primary_key=True)
    _card_id = Column('card_id', String, unique=True)

    @property
    def card_id(self):
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
    __tablename__ = 'groups'

    id = Column(Integer, unique=True, autoincrement=True)
    name = Column(String, primary_key=True)

    students = relationship("Student", secondary=students_groups, lazy='select')
    lessons = relationship("Lesson", lazy='select')

    def __repr__(self):
        return f"<Group(id={self.id}, name={self.name})>"


class Professor(Base):
    __tablename__ = 'professors'

    id = Column(Integer, unique=True, autoincrement=True)
    first_name = Column(String, primary_key=True)
    last_name = Column(String, primary_key=True)
    middle_name = Column(String, primary_key=True)
    _card_id = Column('card_id', String, unique=True)

    lessons: List[Lesson] = relationship("Lesson", back_populates="professor")

    # disciplines
    _disciplines = None

    @property
    def disciplines(self):
        if self._disciplines is None:
            self._disciplines = list(set(map(lambda x: x.discipline, self.lessons)))
        return self._disciplines

    # groups
    _groups = None

    @property
    def groups(self):
        if self._groups is None:
            self._groups = list(set(map(lambda x: x.group, self.lessons)))
        return self._groups

    @property
    def card_id(self):
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


class Update(Base):
    class ActionType(int):
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
        def index():
            max_index = session.query(func.max(Update.id)).first()[0]
            return max_index + 1 if max_index else 0

        update = Update(id=index(),
                        table_name=updated_object.__tablename__,
                        row_id=updated_object.id,
                        action_type=action_type)

        session.add(update)

        return update


class Visitation(Base):
    __tablename__ = 'visitations'

    id = Column(Integer, unique=True, autoincrement=True)
    student_id = Column(Integer, ForeignKey('students.id'), primary_key=True)
    lesson_id = Column(Integer, ForeignKey('lessons.id'), primary_key=True)

    lesson = relationship("Lesson", lazy='joined')
    student = relationship("Student", lazy='select')

    def _create_update(self, action_type=Update.ActionType.UPDATE):
        update = Update.new(self, action_type)

        professors = session.query(Professor). \
            join(Lesson). \
            join(Visitation). \
            filter(Visitation.id == self.id).all()

        update.professors.extend(professors)
        pass

    @staticmethod
    def new(student: Student, lesson: Lesson):
        def calculate_id():
            import time
            value = (lesson.id * pow(10, 6) + student.id) * pow(10, 8) + int(time.time() % (3.154 * pow(10, 7)))
            return value

        row_id = calculate_id()

        visit = Visitation(student_id=student.id, lesson_id=lesson.id, id=row_id)

        try:
            session.add(visit)

            visit._create_update()

            session.commit()
        except sqlalchemy.orm.exc.FlushError:
            session.rollback()
            raise VisitationAlreadyExist()

    def delete(self):
        self._create_update(Update.ActionType.DELETE)
        session.delete(self)
        session.commit()

    def __repr__(self):
        return f'<Visitation(student_id={self.student_id}, lesson_id={self.lesson_id})>'


Session = sessionmaker(bind=engine)
session = Session()

if __name__ == '__main__':
    updates = session.query(Professor).filter(Professor.id == 1).first().updates
    print(updates)
    try:
        student = session.query(Student).first()
        lesson = session.query(Lesson).filter(Lesson.id == 8).first()
        print(session.query(Visitation).
              filter(Visitation.student_id == student.id).
              filter(Visitation.lesson_id == lesson.id).first())

        Visitation.new(student, lesson)
        lesson = session.query(Lesson).filter(Lesson.id == 8).first()
        print(session.query(Visitation).
              filter(Visitation.student_id == student.id).
              filter(Visitation.lesson_id == lesson.id).first())

        print(lesson)
    except VisitationAlreadyExist:
        print('visit exist')
    updates = session.query(Professor).filter(Professor.id == 1).first().updates
    print(updates)
