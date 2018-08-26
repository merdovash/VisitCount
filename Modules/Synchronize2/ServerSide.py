from typing import Dict, Any

from Modules import Module
from Modules.Synchronize2 import address


class Synchronize2Module(Module):
    def __init__(self, app, request, db):
        super().__init__(app, request, db, address)

    def post(self, data, response, auth, **kwargs):
        self.db.remove_updates(auth.user_id)
        response.set_data(self.make_response())

    def make_response(self)->Dict[str, Any]:
        return {'updates_send': self.db.}