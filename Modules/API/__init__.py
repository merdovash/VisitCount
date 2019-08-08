from Modules import Module


def init(app, request):
    from Modules.API.Group import GroupApi
    for init_api in [GroupApi]:
        init_api(app, request)


class API(Module):
    def __init__(self, app, request, address):
        super().__init__(app, request, '/api' + address)
