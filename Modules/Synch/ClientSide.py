from Client.Requests.ClientConnection import ServerConnection
from DataBase2 import Session, ActionType
from Domain.Action import SynchAction
from Domain.functools.Dict import to_dict
from Modules.Synch import address


class Synch(ServerConnection):
    def __init__(self, login, password, host, updates, data, **kwargs):
        super().__init__(login, password, host + address, **kwargs)
        self.data = data
        self.updates = list(map(lambda update: to_dict(update), updates))

    def _run(self):
        self.session = Session()
        self._send({
            'data': self.data,
        })

    def on_response(self, data):
        print('news_mappings', data)

        SynchAction.apply_new_indexes(new=data, old=self.data[ActionType.NEW], session=self.session)

        SynchAction.delete_synchronized_updates(self.updates)

        self.on_finish()
