from DataBase.sql_handler import DataBase
from Modules import Module
from Modules.Synchronize import address


class SynchronizeModule(Module):
    def __init__(self, app, request, db: DataBase):
        super().__init__(app, request, db, address)

    def post(self, data, response, auth, **kwargs):
        if auth.user_type == 1:
            self.accept_new_data(data, auth.user_id)

            updates = self.prepare_updates(auth.user_id)

            response.set_data(updates)
        else:
            response.set_error("no such privileges")

    def accept_new_data(self, data, professor_id):
        self.db.set_updates(data, professor_id)

    def prepare_updates(self, professor_id)->dict:
        return self.db.get_updates(professor_id)
