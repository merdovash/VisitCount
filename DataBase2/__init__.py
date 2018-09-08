from sqlalchemy import Column, Integer, String, ForeignKey, DateTime
from sqlalchemy import create_engine, Table
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship

engine = create_engine('sqlite:///db.db', echo=True)

Base = declarative_base()

students_groups = Table('students_groups', Base.metadata,
                        Column('student_id', Integer, ForeignKey('students.id')),
                        Column('group_id', Integer, ForeignKey('groups.id')))

professors_updates = Table('professors_updates', Base.metadata,
                           Column('professor_id', Integer, ForeignKey('professors.id')),
                           Column('update_id', Integer, ForeignKey('updates.id')))


class Auth(Base):
    __tablename__ = 'auth5'

    id = Column(Integer)
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


class Student(Base):
    __tablename__ = 'students'

    id = Column(Integer, primary_key=True)
    first_name = Column(String)
    last_name = Column(String)
    middle_name = Column(String)
    _card_id = Column('card_id', String)

    @property
    def card_id(self):
        return self._card_id

    @card_id.setter
    def card_id(self, value):
        self._card_id = value
        Update.new(self)
        session.commit()

    groups = relationship("Group", secondary=students_groups, lazy='select')

    def __repr__(self):
        return f"<Student(id={self.id}, card_id={self.card_id}, last_name={self.last_name}, " \
               f"first_name={self.first_name}, middle_name={self.middle_name})>"


class Group(Base):
    __tablename__ = 'groups'

    id = Column(Integer, primary_key=True)
    name = Column(String)

    students = relationship("Student", secondary=students_groups, lazy='select')
    lessons = relationship("Lesson", lazy='select')

    def __repr__(self):
        return f"<Group(id={self.id}, name={self.name})>"


class Professor(Base):
    __tablename__ = 'professors'

    id = Column(Integer, primary_key=True)
    first_name = Column(String)
    last_name = Column(String)
    middle_name = Column(String)
    _card_id = Column('card_id', String)

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


class Discipline(Base):
    __tablename__ = 'disciplines'

    id = Column(Integer, primary_key=True)
    name = Column(String)

    def __repr__(self):
        return f"<Group(id={self.id}, name={self.name})>"


class Lesson(Base):
    __tablename__ = 'lessons'

    id = Column(Integer, primary_key=True)

    professor_id = Column(Integer, ForeignKey('professors.id'))
    professor = relationship("Professor", lazy='select')

    group_id = Column(Integer, ForeignKey('groups.id'))
    groups = relationship("Group", lazy='select')

    discipline_id = Column(Integer, ForeignKey('disciplines.id'))
    discipline = relationship("Discipline", lazy='select')

    type = Column(Integer)
    _date = Column('date', DateTime)
    _completed = Column('completed', Integer)
    room_id = Column(String)

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

    def __repr__(self):
        return f"<Lesson(id={self.id}, professor_id={self.professor_id}," \
               f" group_id={self.group_id}, discipline_id={self.discipline_id}, " \
               f"date={self.date}, type={self.type}, completed={self.completed})>"


class Update(Base):
    class ActionType(int):
        UPDATE = 0
        DELETE = 1

    __tablename__ = 'updates'

    id = Column(Integer, autoincrement=True)
    table_name = Column(String, primary_key=True)
    row_id = Column(Integer, primary_key=True)
    action_type = Column(Integer, nullable=False)

    professors = relationship("Professor", secondary=professors_updates)

    def __repr__(self):
        return f"<Update(id={self.id}, table_name={self.table_name}, row_id={self.row_id})>"

    @staticmethod
    def new(updated_object, action_type=ActionType.UPDATE):
        update = Update(table_name=updated_object.__tablename__, row_id=updated_object.id, action_type=action_type)
        session.add(update)


class Visitation(Base):
    __tablename__ = 'visitations'

    id = Column(Integer, unique=True)
    student_id = Column(Integer, ForeignKey('students.id'), primary_key=True)
    lesson_id = Column(Integer, ForeignKey('lessons.id'), primary_key=True)

    lesson = relationship("Lesson", lazy='select')
    student = relationship("Student", lazy='select')

    @staticmethod
    def new(student: Student, lesson: Lesson):
        visit = Visitation(student_id=student.id, lesson_id=lesson.id)
        Update.new(visit)
        session.commit()

    def delete(self):
        Update.new(self, Update.ActionType.DELETE)
        session.delete(self)
        session.commit()

    def __repr__(self):
        return f'<Visitation(student_id={self.student_id}, lesson_id={self.lesson_id})>'


Session = sessionmaker(bind=engine)
session = Session()
