from typing import Dict, List, Callable, Type

from DataBase2 import _DBObject, _DBTrackedObject
from Domain.Structures.DictWrapper import HiddenStructure

DBSlice = Dict[str, List[_DBObject or Dict]]


class TablesData(HiddenStructure):
    def foreach(self, callback: Callable[[Dict, Type[_DBObject]], None]):
        for class_name in self._data:
            class_: Type[_DBTrackedObject] = _DBObject.class_(class_name)

            for item_dict in self._data[class_name]:
                callback({key: class_.column_type(key)(value) for key, value in item_dict.items()}, class_)

    def __init__(self, data: DBSlice):
        self._data: DBSlice = data
