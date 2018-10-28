from Logger import Logger
from Modules import Module
from Modules.Synchronize import address, Key, updates_len


class SynchronizeModule(Module):
    def __init__(self, app, request, ):
        super().__init__(app, request, address)

    def post(self, data, response, auth, **kwargs):
        if auth.user_type == 1:
            self.accept_new_data(data, auth.user_id)

            updates = self.prepare_updates(auth.user_id)

            response.set_data({
                Key.UPDATES: updates,
                Key.SERVER_ACCEPT_UPDATES_COUNT: updates_len(data)
            })
        else:
            response.set_error("no such privileges")

    def accept_new_data(self, data, professor_id):
        Logger.write(str(data))
        self.db.set_updates(data, professor_id)

    def prepare_updates(self, professor_id)->dict:
        return self.db.get_updates(professor_id)
