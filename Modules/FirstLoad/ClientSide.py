from Client.Requests.ClientConnection import ServerConnection
from DataBase.Authentication import Authentication
from DataBase.sql_handler import ClientDataBase
from Modules.FirstLoad import address


class FirstLoad(ServerConnection):
    class AuthType(int):
        ByLogin = 0
        ByCard = 1

    def __init__(self, program: 'MyProgram', db: ClientDataBase, auth: Authentication,
                 login=None, card_id=None, password=None, on_finish: callable = None):
        super().__init__(db=db, auth=auth, url=program['host']+address)

        self.program = program

        self.password = password
        if card_id is not None:
            self.auth_type = FirstLoad.AuthType.ByCard
            self.card_id = card_id
        elif login is not None:
            self.auth_type = FirstLoad.AuthType.ByLogin
            self.login = login
        else:
            raise Exception("expected card_id or login parameter")

        self.on_response = on_finish

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
        self.send(self.get_request_body())

    def on_response(self, data):
        config = self.db.config
        for table in [config.professors,
                      config.students,
                      config.groups,
                      config.students_groups,
                      config.disciplines,
                      config.lessons,
                      config.visitation,
                      config.auth]:
            self.db.loads(table, data[table])

    def on_error(self, msg):
        self.program.window.error.emit(msg)

# if __name__ == "__main__":
#     f = FirstLoad(card_id="61157", password="123456")
#     f.run()
