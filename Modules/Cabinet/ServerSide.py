from DataBase.Authentication import Authentication
from Date import semester_start, week
from Modules import Module
from Modules.Cabinet import address


class CabinetModule(Module):
    def __init__(self, app, request, db):
        super().__init__(app, request, db, address)

    def post(self, data, response, auth: Authentication, **kwargs):
        response.set_data({
            'user': auth.get_user_info(),
            'semester_start': semester_start(),
            'week': week()
        })
