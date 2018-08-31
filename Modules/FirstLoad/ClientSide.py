from Client.IProgram import IProgram
from Client.Requests.ClientConnection import ServerConnection
from DataBase.Authentication import Authentication
from DataBase.ClentDataBase import ClientDataBase
from DataBase.sql_handler import DataBase
from Modules.FirstLoad import address


class FirstLoad(ServerConnection):
    class AuthType(int):
        ByLogin = 0
        ByCard = 1

    def __init__(self, program: IProgram, database: ClientDataBase, auth: Authentication,
                 login=None, card_id=None, password=None, on_finish: callable = lambda *args: None):
        super().__init__(database=database, auth=auth, url=program['host'] + address)

        self.program: IProgram = program

        self.password = password
        if card_id is not None:
            self.auth_type = FirstLoad.AuthType.ByCard
            self.card_id = card_id
        elif login is not None:
            self.auth_type = FirstLoad.AuthType.ByLogin
            self.login = login
        else:
            raise Exception("expected card_id or login parameter")

        self.on_finish = on_finish

    def get_request_body(self):
        if self.auth_type == FirstLoad.AuthType.ByLogin:
            return {'type': 'first',
                    'user': {
                        'login': self.login,
                        'password': self.password
                        }
                    }
        elif self.auth_type == FirstLoad.AuthType.ByCard:
            return {'type': 'first',
                    'user': {
                        'card_id': self.card_id,
                        'password': self.password
                        }
                    }

    def _run(self):
        request = self.get_request_body()
        print(request)
        self._send(request)

    def on_response(self, data):
        for table in [DataBase.Schema.professors.name,
                      DataBase.Schema.students.name,
                      DataBase.Schema.groups.name,
                      DataBase.Schema.students_groups.name,
                      DataBase.Schema.disciplines.name,
                      DataBase.Schema.lessons.name,
                      DataBase.Schema.visitations.name,
                      DataBase.Schema.auth.name]:
            print(f"loading table {table}: {data[table]}")
            self.database.loads(table, data[table])
        self.on_finish()

    def on_error(self, msg):
        self.program.window.error.emit(msg)

# if __name__ == "__main__":
#     f = FirstLoad(card_id="61157", password="123456")
#     f.run()
