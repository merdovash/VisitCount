from datetime import datetime
from pydoc import locate

from Client.Requests.ClientConnection import ServerConnection
from DataBase2 import Session, NotificationParam, Lesson
from Modules.FirstLoad import address


class FirstLoad(ServerConnection):
    class AuthType(int):
        ByLogin = 0
        ByCard = 1

    def __init__(self, host, login, password, **kwargs):
        super().__init__(login, password, host + address, **kwargs)

    def _run(self):
        self._send({})

    def on_response(self, data):

        session = Session()
        for class_name in data.keys():
            if class_name in data.keys():
                mapper = locate(f'DataBase2.{class_name}')
                mappings = data[class_name]
                print(class_name, mapper)

                for item in mappings:
                    for key in ['_created', '_updated', '_deleted', 'date', '_last_update_in', '_last_update_out']:
                        if key in item.keys():
                            if item[key] not in (None, 'None'):
                                item[key] = datetime.strptime(item[key], "%Y-%m-%dT%H:%M:%S")
                            else:
                                item[key] = None
                    for key in ['completed', 'active', '_is_deleted', 'sex']:
                        if key in item.keys():
                            if item[key] == 'None':
                                item[key] = False
                            else:
                                item[key] = bool(int(item[key]))

                session.bulk_insert_mappings(mapper, mappings)

        session.flush()
        session.commit()

        session.expire_all()
        session.close()

        self.on_finish(dict(login=self.login, password=self.password))

# if __name__ == "__main__":
#     f = FirstLoad(card_id="61157", password="123456")
#     f.run()
