from Modules import Module
from Modules.FirstLoad import address


class FirstLoadModule(Module):
    def __init__(self, app, request, db):
        super().__init__(app, request, db, address)

    def func(self, data, response, auth, **kwargs):
        if auth.user_type == 1:
            response.set_data(self.db.get_data_for_client(professor_id=auth.user_id))
        else:
            response.set_error('no such privileges')
