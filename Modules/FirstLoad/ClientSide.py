from datetime import datetime
from pydoc import locate

from Client.Requests.ClientConnection import ServerConnection
from DataBase2 import Session
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
            mapper = locate(f'DataBase2.{class_name}')
            mappings = data[class_name]
            print(class_name, mapper)

            if class_name == 'Lesson':
                for i, item in enumerate(mappings):
                    mappings[i]['date'] = datetime.strptime(item['date'], "%Y-%m-%dT%H:%M:%S")
            if class_name == 'NotificationParam':
                for i, item in enumerate(mappings):
                    mappings[i]['active'] = eval(mappings[i]['active'])

            session.bulk_insert_mappings(mapper, mappings)

        session.flush()
        session.commit()

        session.expire_all()
        session.close()

        self.on_finish(dict(login=self.login, password=self.password))

# if __name__ == "__main__":
#     f = FirstLoad(card_id="61157", password="123456")
#     f.run()
