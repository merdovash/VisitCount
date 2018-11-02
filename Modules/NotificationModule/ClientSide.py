from Client.Requests.ClientConnection import ServerConnection
from Modules.NotificationModule import address


class Notification(ServerConnection):
    def __init__(self, login, password, host, **kwargs):
        super().__init__(login, password, host + address, **kwargs)

    def _run(self):
        self._send({})

    def on_response(self, data):
        self.on_finish()
