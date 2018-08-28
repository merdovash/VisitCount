from typing import Dict, List

from Client.MyQt.Program import MyProgram
from Client.Requests.ClientConnection import ServerConnection
from Client.test import safe
from Modules.Synchronize import address
from Modules.Synchronize2 import updates_len
from Modules.Synchronize2.ClientSide import Synchronize2


class Synchronize(ServerConnection):
    @safe
    def __init__(self, program: MyProgram):
        super().__init__(program.db, program.auth, program['host'] + address)
        self.professor = self._get_professor(program.auth.user_id)
        self.program = program

    @safe
    def _run(self):
        updates = self.database.get_updates(self.auth.user_id)
        self.send_updates = updates_len(updates)
        self._send({"user": self._get_professor(self.auth.user_id),
                   "data": updates})

    @safe
    def on_response(self, data: Dict[str, List[Dict[str, str or int]]]):
        self.database.set_updates(data, self.auth.user_id, False)

        row_affected = updates_len(data)

        Synchronize2(self.program, self.auth, row_affected=row_affected, updates_send=self.send_updates).start()

    @safe
    def on_error(self, msg):
        self.program.window.error.emit(f'В ходе процедуры синхронизации произошла ошибка <br>{msg}')
