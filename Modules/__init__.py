from DataBase.Authentication import Authentication
from Parser.JsonParser import JsonParser
from Server.Response import Response

default_methods = ['POST']


class Module:
    def __init__(self, app, request, db, address, func=None, methods=default_methods, form=False):
        self.db = db
        self._is_form = form
        request_type = address[1:]

        if func is not None:
            self.func = func

        @app.route(address, methods=["POST"], endpoint=address[1:])
        def auth(**kwargs):
            if 'POST' in methods:
                if request.method == 'POST':
                    response = Response(request_type)
                    data = self._read(request)
                    if data is not None:
                        authentication = Authentication(self.db, **data['user'])

                        if authentication.status:
                            self.post(data=data.get('data'), response=response, auth=authentication, **kwargs)
                        else:
                            response.set_error(db.last_error())
                    else:
                        return response.set_error("you send no data: {}".format(request.data))

                    return response()
            if 'GET' in methods:
                pass

    def _read(self, request):
        if self._is_form:
            return {'user': {
                'login': request.form['login'],
                'password': request.form['password']
            },
                'data': {}
            }
        else:
            return JsonParser.read(request.data.decode('utf8').replace("'", '"'))

    def post(self, data: dict, response: Response, auth: Authentication, **kwargs):
        pass
