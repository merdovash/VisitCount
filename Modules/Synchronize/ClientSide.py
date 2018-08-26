from typing import Dict, List

from Client.Requests.ClientConnection import ServerConnection
from DataBase.Authentication import Authentication
from Modules.Synchronize import address
from Modules.Synchronize2 import updates_len
from Modules.Synchronize2.ClientSide import Synchronize2


class Synchronize(ServerConnection):
    def __init__(self, program: 'MyProgram', auth: Authentication):
        super().__init__(program.db, auth, program['host'] + address)
        self.professor = self._get_professor(auth.user_id)
        self.program = program

    def _run(self):
        updates = self.db.get_updates(self.auth.user_id)
        self.send_updates = updates_len(updates)
        self.send({"user": self._get_professor(self.auth.user_id),
                   "data": updates})

    def on_response(self, data: Dict[str, List[Dict[str, str or int]]]):
        self.db.set_updates(data, self.auth.user_id, False)

        row_affected = updates_len(data)

        Synchronize2(self.program, self.auth, row_affected=row_affected, updates_send=self.send_updates).start()




