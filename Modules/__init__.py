from DataBase2 import Auth, Session
from Domain.Exception.Authentication import InvalidLoginException, InvalidPasswordException
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
                        authentication = None
                        try:
                            print(data['user'])
                            authentication = Auth.log_in(**data['user'])

                            self.post(data=data.get('data'), response=response,
                                      auth=authentication, **kwargs)

                        except InvalidLoginException as e:
                            response.set_error(str(e))
                        except InvalidPasswordException as e:
                            response.set_error(str(e))
                        finally:
                            if authentication is not None:
                                authentication.user.session.close()
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

    def read_data(self, data: bytearray):
        return JsonParser.read(data.decode('utf8').replace("'", '"'))


