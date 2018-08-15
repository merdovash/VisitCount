from Modules import Module
from Modules.NewVisits import address


class NewVisitsModule(Module):
    def __init__(self, app, request, db):
        super().__init__(app, request, db, address)

    def func(self, data, response, auth, **kwargs):
        count = self.db.save_new_visits(data['data']['visits'])
        response.set_data(str(count))

