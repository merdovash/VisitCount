"""
Contains all DataBase entities as Classes
"""
from typing import List


class Tables:
    """
    Class contain static tables names
    """

    Parents = "parents"
    ParentsStudents = "parents_students"
    Students = "students"
    Professors = "professors"
    Discipline = "disciplines"
    Groups = "groups"
    Lessons = "lessons"
    Auth = "auth5"
    StudentsGroups = "students_groups"
    Visitations = "visitations"
    Updates = "updates"


class DBType:
    """
    parent DataBase class
    """

    Id = "id"

    def __init__(self, show_id=True, **kwargs):
        self.__rule__ = {}
        if show_id:
            self.__rule__[DBType.Id] = "id"
            if DBType.Id in kwargs.keys():
                self.id = kwargs[DBType.Id]
            else:
                self.id = None

    def __repr__(self):
        return "<{}>".format(
            ', '.join(
                ["{}={}".format(i, self.__getattribute__(self.__rule__[i])) for i in self.__rule__.keys()]
            )
        )

    def __getitem__(self, item):
        if item in self.__rule__.values():
            return self.__getattribute__(item)
        else:
            raise IndexError("no such item: {}".format(item))

    def order(self, order: List[str]) -> List[str or int]:
        """

        returns values in specified order.
        if specified order contains wrong value name then raise IndexError

        :param order: list of values names
        :return: ordered list of values
        """
        l = []
        for o in order:
            if o not in self.__dict__:
                raise IndexError("no such value {}".format(o))
            else:
                l.append(self.__getattribute__(o))
        return l


class _People(DBType):
    """
    private class
    """
    FirstName = "first_name"
    LastName = "last_name"
    MiddleName = "middle_name"

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.__rule__[_People.FirstName] = "first_name"
        self.first_name = kwargs.get(_People.FirstName, None)

        self.__rule__[_People.LastName] = "last_name"
        self.last_name = kwargs.get(_People.LastName, None)

        self.__rule__[_People.MiddleName] = "middle_name"
        self.middle_name = kwargs.get(_People.MiddleName, None)


class _CardOwner(_People):
    CardId = "card_id"

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.__rule__[_CardOwner.CardId] = "card_id"
        self.card_id = kwargs.get(_CardOwner.CardId, None)


class _Nameable(DBType):
    Name = "name"

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.__rule__[_Nameable.Name] = "name"
        self.name = kwargs.get(_Nameable.Name, None)


class Parent(_People):
    Email = "email"

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.__rule__[Parent.Email] = "email"
        self.email = kwargs.get(Parent.Email, None)


class Student(_CardOwner):
    pass


class Professor(_CardOwner):
    pass


class Discipline(_Nameable):
    pass


class Group(_Nameable):
    pass


class Lesson(DBType):
    ProfessorId = "professor_id"
    GroupId = "group_id"
    DisciplineId = "discipline_id"
    Date = "date"
    Completed = "completed"
    Room = "room_id"
    Type = "type"

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.__rule__[Lesson.ProfessorId] = "professor_id"
        self.professor_id = kwargs.get(Lesson.ProfessorId, None)

        self.__rule__[Lesson.GroupId] = "group_id"
        self.group_id = kwargs.get(Lesson.GroupId, None)

        self.__rule__[Lesson.DisciplineId] = "discipline_id"
        self.discipline_id = kwargs.get(Lesson.DisciplineId, None)

        self.__rule__[Lesson.Date] = "date"
        self.date = kwargs.get(Lesson.Date, None)

        self.__rule__[Lesson.Completed] = "completed"
        self.completed = kwargs.get(Lesson.Completed, None)

        self.__rule__[Lesson.Room] = "room_id"
        self.room_id = kwargs.get(Lesson.Room, None)

        self.__rule__[Lesson.Type] = "type"
        self.type = kwargs.get(Lesson.Type, None)


class Visitation(DBType):
    LessonId = "lesson_id"
    StudentId = "student_id"

    def __init__(self, **kwargs):
        super().__init__(False, **kwargs)

        self.__rule__[Visitation.LessonId] = "lesson_id"
        self.lesson_id = kwargs.get(Visitation.LessonId, None)

        self.__rule__[Visitation.StudentId] = "student_id"
        self.student_id = kwargs.get(Visitation.StudentId, None)


class LessonType(int):
    Lecture = 0
    LaboratoryWork = 1
    PracticalWork = 2
