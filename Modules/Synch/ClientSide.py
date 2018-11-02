from Client.Requests.ClientConnection import ServerConnection
from DataBase2 import Update, create_threaded
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
        new_items_map_after = data

        Session, _, _, _ = create_threaded()

        session = Session()

        for key in new_items_map_before.keys():
            item = new_items_map_before[key]
            new_id = int(new_items_map_after[str(key)])

            if item.id != new_id:
                print(f'item {item} gets new id={new_id}')
                session.execute(
                    "UPDATE {table_name} SET id={id} WHERE id={old_id}".format(
                        table_name=item.__tablename__,
                        id=new_id,
                        old_id=item.id
                    )
                )
        else:
            session.commit()

        session.query(Update).delete()
        session.commit()

        Session.remove()

        print(new_items_map_before, new_items_map_after)

        self.on_finish()
