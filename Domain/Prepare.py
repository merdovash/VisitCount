from collections import defaultdict

from DataBase2 import Update, UpdateType
from Parser.JsonParser import Base_to_dict


def get_updated_object(update: Update, session):
    exec(f'from DataBase2 import {update.table_name}')
    type_ = eval(update.table_name)
    obj = session.query(type_).filter(type_.id == update.row_id).first()
    return obj


def updates(session):
    print('making updates data')
    query = session.query(Update)

    new_items_map = dict()
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
                item = Base_to_dict(change)
                if action_type == UpdateType.NEW:
                    item['new_index'] = i
                    new_items_map[i] = change
                changes_dict[type(change).__name__].append(item)

        if len(changes_dict) > 0:
            print(changes_dict)
            total_dict[action_type] = changes_dict

        print(total_dict)
    return dict(new_items_map=new_items_map,
                total_dict=total_dict)
