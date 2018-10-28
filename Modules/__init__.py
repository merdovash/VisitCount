from DataBase2 import Auth, Session, ProfessorSession
from Exception import NoSuchUserException
from Parser.JsonParser import JsonParser
from Server.Response import Response

default_methods = ['POST']


class Keys(str):
    pass


class Module:
    def __init__(self, app, request, address, func=None,
                 methods=default_methods, form=False):
        self._is_form = form

        self.db = None
        request_type = address[1:]

        if func is not None:
            self.func = func

        @app.route(address, methods=["POST"], endpoint=address[1:])
        def auth(**kwargs):
            self.db = Session()
            if 'POST' in methods:
                if request.method == 'POST':
                    response = Response(request_type)
                    data = self._read(request)
                    if data is not None:
                        try:
                            print(data['user'])
                            authentication = Auth.log_in(**data['user'],
                                                         session=self.db)

                            self.db = ProfessorSession(authentication.user.id, self.db)
                            self.post(data=data.get('data'), response=response,
                                      auth=authentication, **kwargs)

                        except NoSuchUserException as e:
                            response.set_error('No such user')
                    else:
                        response.set_error(
                            "you send no data: {}".format(request.value))

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
            print(request.data)
            return JsonParser.read(
                request.data.decode('utf8').replace("'", '"'))

    def post(self, data: dict, response: Response, auth: Auth, **kwargs):
        pass
