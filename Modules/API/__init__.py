from Modules import Module


def init(app, request):
    from Modules.API.Group import GroupApi
    from Modules.API.Professor import ProfessorSettingsApi

    for init_api in [GroupApi, ProfessorSettingsApi]:
        init_api(app, request, init_api.address)


class API(Module):
    address = '/api'

    def __init__(self, app, request, address):
        super().__init__(app, request, address)
