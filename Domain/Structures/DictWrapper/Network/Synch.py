from datetime import datetime
from typing import Dict, List, Callable, Type

from DataBase2 import ISynchronize, DBObject
from Domain.Structures.DictWrapper import HiddenStructure, Structure
from Domain.Structures.DictWrapper.Network import TablesData
from Domain.Validation import Values
from Domain.Validation.Values import Get


class ChangeId(Structure):
    from_id: int
    to_id: int

    def __init__(self, from_id, to_id):
        self.from_id = Values.Get.int(from_id)
        self.to_id = Values.Get.int(to_id)


class IDChanges(HiddenStructure):
    def __init__(self, data):
        self._data: Dict[str, List[ChangeId]] = {key: [ChangeId(**i) for i in value]
                                                 for key, value in data.items()}

    def foreach(self, func: Callable[[ChangeId, Type[ISynchronize]], None]):
        for class_name in self._data:
            class_: Type[ISynchronize] = DBObject.class_(class_name)

            for item in self._data[class_name]:
                func(item, class_)


class Changes(Structure):
    created: TablesData
    updated: TablesData
    deleted: TablesData

    def __init__(self, created, updated, deleted):
        self.created = TablesData(created)
        self.updated = TablesData(updated)
        self.deleted = TablesData(deleted)

    def __len__(self):
        return len(self.created)+len(self.updated)+len(self.deleted)


class ClientUpdateData(Structure):
    updates: Changes
    last_update_out: datetime
    last_update_in: datetime

    def __init__(self, updates, last_update_in, last_update_out):
        if isinstance(updates, Changes):
            self.updates = updates
        else:
            self.updates = Changes(**updates)

        self.last_update_in = Get.datetime(last_update_in)

        self.last_update_out = Get.datetime(last_update_out)


class ServerUpdateData(Structure):
    changed_id: IDChanges
    updates: Changes
    skiped: TablesData

    def __init__(self, changed_id, updates, skiped):
        self.changed_id = IDChanges(changed_id)

        if isinstance(updates, Changes):
            self.updates = updates
        else:
            self.updates = Changes(**updates)

        if isinstance(skiped, TablesData):
            self.skiped = skiped
        else:
            self.skiped = TablesData(skiped)
