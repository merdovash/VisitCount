from typing import Dict, List, Callable, Type

from DataBase2 import _DBObject, _DBTrackedObject, StudentsGroups, Student, Group, Discipline, Professor, Auth, \
    LessonsGroups, Lesson, Visitation, Administration, Parent, StudentsParents, _DBPerson, Semester, Faculty, \
    Department, DepartmentProfessors, DataView, ContactInfo, ContactViews, LessonType, Room, Building
from Domain.Structures.DictWrapper import HiddenStructure, Structure

DBSlice = Dict[str, List[_DBObject or Dict]]


class TablesData(HiddenStructure):
    DEFAULT_ORDER = [i.__name__ for i in [
        DataView,
        ContactInfo,
        ContactViews,
        Faculty,
        Department,
        Auth,
        Professor,
        DepartmentProfessors,
        Discipline,
        Group,
        Student,
        StudentsGroups,
        Semester,
        Building,
        Room,
        LessonType,
        Lesson,
        LessonsGroups,
        Visitation,
        Administration,
        Parent,
        StudentsParents
    ]]

    def foreach(self, callback: Callable[[Dict, Type[_DBObject]], None]):
        for class_name in (self.DEFAULT_ORDER if not self._reverse else reversed(self.DEFAULT_ORDER)):
            if class_name in self._data.keys():
                class_: Type[_DBTrackedObject] = _DBObject.class_(class_name)

                for item_dict in self._data[class_name]:
                    if item_dict is not None:
                        callback({key: class_.column_type(key)(value) for key, value in item_dict.items()}, class_)

    def __init__(self, data: DBSlice, reverse=False):
        self._reverse = reverse
        self._data: DBSlice = data


class BaseRequest(Structure):
    user: Dict
    data: Dict

    def __init__(self, user: _DBPerson, data=None):
        self.user = {
            'login': user.auth.login,
            'password': user.auth.password,
            'user_type': user.auth.user_type
        }
        self.data = data
