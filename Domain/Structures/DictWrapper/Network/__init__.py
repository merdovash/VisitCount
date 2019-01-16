from typing import Dict, List, Callable, Type

from DataBase2 import _DBObject, _DBTrackedObject, StudentsGroups, Student, Group, Discipline, Professor, Auth, \
    LessonsGroups, Lesson, Visitation, Administration, NotificationParam, Parent, StudentsParents
from Domain.Structures.DictWrapper import HiddenStructure

DBSlice = Dict[str, List[_DBObject or Dict]]


class TablesData(HiddenStructure):
    DEFAULT_ORDER = [i.__name__ for i in [
        Auth,
        Professor,
        Discipline,
        Group,
        Student,
        StudentsGroups,
        Lesson,
        LessonsGroups,
        Visitation,
        Administration,
        NotificationParam,
        Parent,
        StudentsParents
    ]]

    def foreach(self, callback: Callable[[Dict, Type[_DBObject]], None]):
        for class_name in self.DEFAULT_ORDER:
            if class_name in self._data.keys():
                class_: Type[_DBTrackedObject] = _DBObject.class_(class_name)

                for item_dict in self._data[class_name]:
                    callback({key: class_.column_type(key)(value) for key, value in item_dict.items()}, class_)

    def __init__(self, data: DBSlice):
        self._data: DBSlice = data
