from DataBase.Authentication import Authentication
from Parser.JsonParser import jsonParser
from Server.Response import Response

default_methods = ['POST']


class Module:
    def __init__(self, app, request, db, address, func=None, methods=default_methods):
        self.request = request
        self.db = db

        if func is not None:
            self.func = func

        @app.route(address, methods=["POST"], endpoint=address[1:])
        def auth(**kwargs):
            if 'POST' in methods:
                if self.request.method == 'POST':
                    data = jsonParser.read(self.request.data.decode('utf8').replace("'", '"'))
                    response = Response('data')
                    authentication = Authentication(self.db, **data['user'])

                    if authentication.status:
                        self.post(data=data['data'], response=response, auth=authentication, **kwargs)
                    else:
                        response.set_error('auth failed')
                    return response()
            if 'GET' in methods:
                pass

    def post(self, data, response, auth, **kwargs):
        pass
