from Client.Requests.ClientConnection import ServerConnection
from DataBase2 import Update, create_threaded
from Domain.functools.Dict import fix_keys
from Modules.Synch import address


class Synch(ServerConnection):
    def __init__(self, login, password, host, data, **kwargs):
        super().__init__(login, password, host + address, **kwargs)
        self.updates = data

    def _run(self):
        self._send({
            'data': self.updates,
        })

    def on_response(self, data):
        new_items_map_before = self.updates['new_items_map']
        new_items_map_after = fix_keys(data)

        Session, _, _, _ = create_threaded()

        session = Session()

        for table in new_items_map_before.dict.keys():
            new_items = new_items_map_before.dict[table]

            if len(new_items) > 0:
                for item in new_items:
                    session.merge(item)
                    item.id = new_items_map_after[new_items_map_before.index(item)]

                session.commit()
        else:
            session.commit()

        session.query(Update).delete()
        session.commit()

        Session.remove()

        print(new_items_map_before, new_items_map_after)

        self.on_finish()
