from Modules import Module
from Modules.Synchronize import address


class SynchronizeModule(Module):
    def __init__(self, app, request, db):
        super().__init__(app, request, db, address)

    def func(self, data, response, auth, **kwargs):
        auth = kwargs.get('auth')
        if auth.user_type == 1:
            response.set_data(self.db.get_updates(auth.user_id))
        else:
            response.set_error("no such privileges")
