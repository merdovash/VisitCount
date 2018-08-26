from Client.MyQt.Program import MyProgram
from Client.Requests.ClientConnection import ServerConnection
from DataBase.Authentication import Authentication
from Modules.Synchronize2 import address


class Synchronize2(ServerConnection):
    def __init__(self, program: MyProgram, auth: Authentication, row_affected: int, updates_send: int):
        super().__init__(program.db, auth, program['host'] + address)
        self.row_affected = row_affected
        self.updates_send = updates_send
        self.program = program

    def _run(self):
        request = {
            'user': self._get_professor(self.auth.user_id),
            'data': {
                'row_affected': self.row_affected
            }
        }
        self.send(request)

    def on_response(self, data):
        if data['updates_send'] == self.updates_send:
            self.db.remove_updates(self.auth.user_id)
        else:
            self.program.window.error.emit("Во время синхронизации произошла ошибка. <br>"
                                           "Синхронизация будет произведена повтроно.")
