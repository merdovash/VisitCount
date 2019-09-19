import traceback

from DataBase2 import Auth, Session
from Domain.Exception.Authentication import InvalidLoginException, InvalidPasswordException
from Parser.JsonParser import JsonParser
from Server.Response import Response

default_methods = ['POST']


class Module:
    """
    Абстрактный класс
    Определяет программный интерфейс модуля системы

    Скрывает в себе следующие функции:
        - аутентификация пользователя
        - распаковка сообщения
        - упакаовка сообщения
    """

    __auth_require__ = True

    def __init__(self, app, request, address, func=None, methods=default_methods, form=False):
        self._is_form = form

        self.session = None
        request_type = address[1:]

        if func is not None:
            self.func = func

        print(f'bind {address} to {address[1:]}')

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
                            if self.__auth_require__:
                                authentication = Auth.log_in(**data['user'])

                            result = self.post(data=data.get('data'), auth=authentication, **kwargs)

                            response.set_data(result)
                        except Exception as e:
                            response.set_error(f'{str(type(e))}: {str(e)}')
                            traceback.print_exc(10)

                        finally:
                            if authentication is not None:
                                authentication.user.session().close()
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
            return self.__read_data(request.data)

    def post(self, data: dict, auth: Auth, **kwargs):
        pass

    def __read_data(self, data: bytearray):
        return JsonParser.read(data.decode('utf8').replace("'", '"'))


