from typing import Dict, Any

from Client.Domain import Load
from Client.IProgram import IProgram
from Client.Requests.ClientConnection import ServerConnection
from Client.test import safe
from DataBase2 import Update
from Modules.Synchronize import address, updates_len, Key
from Modules.Synchronize2.ClientSide import Synchronize2


class Synchronize(ServerConnection):
    @safe
    def __init__(self, program: IProgram):
        super().__init__(program.auth, program['host'] + address)
        self.program: IProgram = program

        self.updates = Update.all()
        self.send_updates = len(self.updates)

    @safe
    def _run(self):
        self._send({"user": self.get_user(),
                    "data": self.send_updates})

    @safe
    def on_response(self, data: Dict[str, Any]):
        print(data)
        if self._check(data[Key.SERVER_ACCEPT_UPDATES_COUNT]):

            Update.delete()

            Load.loads(data)

            accepted_updates_count = updates_len(data[Key.UPDATES])

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
