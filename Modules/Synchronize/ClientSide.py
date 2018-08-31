from typing import Dict, Any

from Client.Requests.ClientConnection import ServerConnection
from Client.test import safe
from Modules.Synchronize import address, updates_len, Key
from Modules.Synchronize2.ClientSide import Synchronize2


class Synchronize(ServerConnection):
    @safe
    def __init__(self, program):
        super().__init__(program.db, program.auth, program['host'] + address)
        self.professor = self.get_user(program.auth.user_id)
        self.program = program

    @safe
    def _run(self):
        updates, self.send_updates = self.database.get_updates(self.auth.user_id)
        self._send({"user": self.get_user(self.auth.user_id),
                   "data": updates})

    @safe
    def on_response(self, data: Dict[str, Any]):
        if self._check(data[Key.SERVER_ACCEPT_UPDATES_COUNT]):

            self.database.remove_updates(self.auth.user_id)

            self.database.set_updates(data[Key.UPDATES], self.auth.user_id, False)

            accepted_updates_count = updates_len(data)

            Synchronize2(self.program,
                         self.auth,
                         row_affected=accepted_updates_count,
                         updates_send=self.send_updates).start()
        else:
            self.on_error('Сервер неверно принял отправленные данные. Попробуйте снова.')

    @safe
    def on_error(self, msg):
        self.program.window.error.emit(f'В ходе процедуры синхронизации произошла ошибка <br>{msg}')

    def _check(self, server_accept_updates_count):
        return self.send_updates == server_accept_updates_count
