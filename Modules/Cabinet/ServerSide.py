from DataBase2 import Auth
from Date import semester_start, week
from Modules import Module
from Modules.Cabinet import address


class CabinetModule(Module):
    def __init__(self, app, request, ):
        super().__init__(app, request, address)

    def post(self, data, response, auth: Auth, **kwargs):
        response.set_data({
            'user': auth.get_user_info(),
            'semester_start': semester_start(),
            'week': week()
        })
