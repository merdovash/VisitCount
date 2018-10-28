from collections import defaultdict

from Client.IProgram import IProgram
from Client.Requests.ClientConnection import ServerConnection
from DataBase2 import Auth, Update, Session
from Modules.Synch import address
from Parser.JsonParser import Base_to_dict


class Synch(ServerConnection):
    def __init__(self, auth: Auth, program: IProgram):
        super().__init__(auth, address, program)
        self._session = None
        self.new_items_map = {}

    def _run(self):
        self.data = self.get_synch_data()
        self._send({
            'user': self.get_auth(),
            'data': self.data,
        })

    def session(self):
        if self._session is None:
            self._session = Session()
        return self._session

    def get_synch_data(self) -> dict:
        def f(update: Update):
            exec(f'from DataBase2 import {update.table_name}')
            type_ = eval(update.table_name)
            obj = self.session().query(type_).filter(type_.id == update.row_id).first()
            return obj

        total_dict = {Update.ActionType.UPDATE: None,
                      Update.ActionType.NEW: None,
                      Update.ActionType.DELETE: None}

        for action_type in [Update.ActionType.UPDATE, Update.ActionType.NEW, Update.ActionType.DELETE]:
            updates_list = self.session().query(Update).filter(Update.action_type == action_type).all()

            changes_dict = defaultdict(list)

            for i, update in enumerate(updates_list):
                change = f(update)

                if change is not None:
                    item = Base_to_dict(change)
                    if action_type == Update.ActionType.NEW:
                        item['new_index'] = i
                        self.new_items_map[i] = change
                    changes_dict[type(change).__name__].append(item)

                else:
                    self.session().delete(update)

            if len(changes_dict) > 0:
                total_dict[action_type] = changes_dict
            else:
                total_dict[action_type] = []

        print(total_dict)
        print(self.new_items_map)
        return total_dict
