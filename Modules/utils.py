from typing import Callable, Dict, Type, List

import DataBase2
from DataBase2 import Auth, ISession
from Modules.API import AccessError


DEFAULT_ORDER = [i.__name__ for i in [
    DataBase2.DataView,
    DataBase2.Contact,
    DataBase2.ContactViews,
    DataBase2.Faculty,
    DataBase2.Department,
    DataBase2.Auth,
    DataBase2.Professor,
    DataBase2.DepartmentProfessors,
    DataBase2.Discipline,
    DataBase2.Group,
    DataBase2.Student,
    DataBase2.StudentsGroups,
    DataBase2.Semester,
    DataBase2.Building,
    DataBase2.Room,
    DataBase2.LessonType,
    DataBase2.Lesson,
    DataBase2.LessonsGroups,
    DataBase2.Visitation,
    DataBase2.Administration,
    DataBase2.Parent,
    DataBase2.StudentsParents
]]


def zone_access(zone):
    def decorator(func):
        def __wrapper__(self, data: dict, auth: Auth, **kwargs):
            if auth.has_access(zone):
                return func(self, data, auth, **kwargs)

            raise AccessError()

        return __wrapper__
    return decorator


def synch_foreach(session: ISession, data: Dict[str, List],
                  func: Callable[[ISession, Dict, Type[DataBase2.DBObject]], None]):
    for class_name in DEFAULT_ORDER:
        if class_name in data.keys():
            class_: Type[DataBase2.DBObject] = DataBase2.DBObject.class_(class_name)

            for item_dict in data[class_name]:
                if item_dict is not None:
                    func(session, item_dict, class_)

            session.flush()
