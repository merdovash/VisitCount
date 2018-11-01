from Client.Requests.ClientConnection import ServerConnection
from Modules.Synch import address


class Synch(ServerConnection):
    def __init__(self, login, password, host, data, **kwargs):
        super().__init__(login, password, host + address, **kwargs)
        self.updates = data

    def _run(self):
        self._send({
            'data': self.updates,
        })
