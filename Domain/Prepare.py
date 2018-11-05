from collections import defaultdict

import DataBase2
from DataBase2 import Update, UpdateType
from Parser.JsonParser import Base_to_dict, JsonParser


class NewIDMap:
    def __init__(self, f=None):
        self.dict = {
            type(x).__name__: []
            for x in (DataBase2.Discipline(),
                      DataBase2.Student(),
                      DataBase2.StudentsGroups(),
                      DataBase2.Group(),
                      DataBase2.Professor(),
                      DataBase2.Lesson(),
                      DataBase2.Visitation(),
                      DataBase2.Parent(),
                      DataBase2.Administration(),
                      DataBase2.NotificationParam()
                      )
        }
        self.list = []
        self._list = []

        if f is not None:
            for item in f.items():
                self.append(item)

    def __getitem__(self, item):
        return self.dict[item]

    def __setitem__(self, key, value):
        self.dict[key] = value

    def append(self, table, item, mapping):
        self.dict[table].append(item)
        self.list.append(mapping)
        self._list.append(item)

    def get(self, i):
        return self.list[i]

    def index(self, item):
        if isinstance(item, dict):
            return self.list.index(item)
        elif isinstance(item, DataBase2.Base):
            return self._list.index(item)

    def to_json(self):
        return JsonParser.dump({'index': self.list})

    def keys(self):
        return range(len(self.list))


def get_updated_object(update: Update, session):
    exec(f'from DataBase2 import {update.table_name}')
    type_ = eval(update.table_name)
    obj = session.query(type_).filter(type_.id == update.row_id).first()
    return obj


def updates(session):
    print('making updates data')
    query = session.query(Update)

    new_items_map = NewIDMap()
    total_dict = {UpdateType.UPDATE: {},
                  UpdateType.NEW: {},
                  UpdateType.DELETE: {}}

    for action_type in [UpdateType.UPDATE, UpdateType.NEW, UpdateType.DELETE]:
        updates_list = query.filter_by(action_type=action_type).all()

        print(updates_list)

        changes_dict = defaultdict(list)

        for i, update in enumerate(updates_list):
            change = get_updated_object(update, session)

            if change is not None:
                mapping = Base_to_dict(change)
                if action_type == UpdateType.NEW:
                    new_items_map.append(update.table_name, change, mapping)
                    mapping['new_index'] = new_items_map.index(mapping)
                changes_dict[type(change).__name__].append(mapping)

        if len(changes_dict) > 0:
            print(changes_dict)
            total_dict[action_type] = changes_dict

        print(total_dict)
    return dict(new_items_map=new_items_map,
                total_dict=total_dict)
