from DataBase2 import Auth, Session, ProfessorSession
from Domain import Action
from Domain.Action import InvalidLogin, InvalidPassword
from Parser.JsonParser import JsonParser
from Server.Response import Response

default_methods = ['POST']


class Keys(str):
    pass


class Module:
    def __init__(self, app, request, address, func=None,
                 methods=default_methods, form=False):
        self._is_form = form

        self.session = None
        request_type = address[1:]

        if func is not None:
            self.func = func

        @app.route(address, methods=["POST"], endpoint=address[1:])
        def auth(**kwargs):
            self.session = Session()
            if 'POST' in methods:
                if request.method == 'POST':
                    response = Response(request_type)
                    data = self._read(request)
                    if data is not None:
                        try:
                            print(data['user'])
                            authentication = Action.log_in(**data['user'], session=self.session)

                            self.session = ProfessorSession(authentication.user.id, self.session)
                            self.post(data=data.get('data'), response=response,
                                      auth=authentication, **kwargs)

                        except InvalidLogin as e:
                            response.set_error(str(e))
                        except InvalidPassword as e:
                            response.set_error(str(e))
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
            return self.read_data(request.data)

    def post(self, data: dict, response: Response, auth: Auth, **kwargs):
        pass

    def read_data(self, data: str):
        return JsonParser.read(data.decode('utf8').replace("'", '"'))
