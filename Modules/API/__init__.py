from Modules import Module


class APIError(Exception):
    def __init__(self, msg):
        super().__init__(msg)


class AccessError(APIError):
    def __init__(self, msg='Недостаточно прав'):
        super().__init__(msg)


class NoDataError(APIError):
    pass


def init(app, request):
    from Modules.API.Group import GroupAPI
    from Modules.API.User.FirstLoad import FirstLoad
    from Modules.API.User.Professor.NewProfessor import ProfessorCreateAPI
    from Modules.API.User.Settings import SettingsAPI

    for init_api in [GroupAPI, SettingsAPI, FirstLoad, ProfessorCreateAPI]:
        init_api(app, request, init_api.__address__)


class API(Module):
    __address__ = '/api'

    def __init__(self, app, request, address):
        super().__init__(app, request, address)
