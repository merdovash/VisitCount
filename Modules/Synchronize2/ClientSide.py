from Client.Program import MyProgram
from Client.Requests.ClientConnection import ServerConnection
from Client.test import safe
from DataBase.Authentication import Authentication
from Modules.Synchronize2 import address, Key


class Synchronize2(ServerConnection):
    @safe
    def __init__(self, program: MyProgram, auth: Authentication, row_affected: int, updates_send: int):
        super().__init__(program.db, auth, program['host'] + address)
        self.row_affected = row_affected
        self.updates_send = updates_send
        self.program = program

    @safe
    def _run(self):
        request = {
            'user': self.get_user(self.auth.user_id),
            'data': {
                Key.CLIENT_ACCEPT_UPDATES_COUNT: self.row_affected
            }
        }
        self._send(request)

    @safe
    def on_response(self, data):
        self.program.window.msg.emit('Синхронизация прошла успешно')

    @safe
    def on_error(self, msg):
        self.program.window.error.emit(msg)
