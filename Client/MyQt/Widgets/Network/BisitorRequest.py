from urllib.parse import urlparse

from PyQt5.QtCore import QUrl, pyqtSignal
from PyQt5.QtNetwork import QNetworkRequest, QNetworkAccessManager, QNetworkReply
from PyQt5.QtWidgets import QMessageBox

from DataBase2 import Auth, _DBPerson
from Parser import Args
from Parser.JsonParser import JsonParser
from Server.Response import Response


def pack(user, data):
    return dict(user=user.auth.data(), data=data)


def get_full_address(address) -> str:
    u = urlparse(address)

    if not u.netloc:
        u = u._replace(netloc=Args().host)

    if not u.scheme:
        u = u._replace(scheme='http')

    return u.geturl()


class _QBisitorRequest(QNetworkRequest):
    def __init__(self, *__args):
        super().__init__(*__args)
        self.setHeader(QNetworkRequest.ContentTypeHeader, "application/json")


class QBisitorAccessManager(QNetworkAccessManager):
    response = pyqtSignal('PyQt_PyObject')
    error = pyqtSignal('PyQt_PyObject')

    def __init__(self, user, response_type):
        super().__init__()

        if user is not None:
            if isinstance(user, Auth):
                self.data = {
                    'user': user.data()
                }
            elif issubclass(type(user), _DBPerson):
                self.data = {
                    'user': user.auth.data()
                }
            else:
                raise TypeError(type(user))
        else:
            self.data = {}
        self.response_type = response_type
        self.finished.connect(self.on_finish)

    def post(self, request: QNetworkRequest, data=None, *__args):
        self.data['data'] = data
        print('request', request.url())
        q_data = bytearray(JsonParser.dump(self.data), encoding='utf-8')
        return super().post(request, q_data, *__args)

    def on_finish(self, reply: QNetworkReply):
        if reply.error() == QNetworkReply.NoError:
            bytes_string = reply.readAll()
            data = JsonParser.read(str(bytes_string, 'utf-8'))
            response = Response.load(**data, class_=self.response_type)
            if response.status == response.Status.OK:
                self.response.emit(response.data)
            else:
                self.error.emit(response)
        else:
            QMessageBox().information(None, "Загрузка информации с сервера",
                                      f"Сервер не смог ответить на запрос.\n код ошибки: {str(reply.error())}")

        self.deleteLater()


class QBisitorRequest:
    response_type = None

    def __init__(self, address, user, data, *, on_finish, on_error=None, response_type=None):
        self.manager = QBisitorAccessManager(user, response_type if response_type is not None else self.response_type)
        self.request = _QBisitorRequest()
        self.request.setUrl(QUrl(get_full_address(address)))
        self.manager.response.connect(on_finish)
        if on_error is not None:
            self.manager.error.connect(on_error)
        else:
            self.manager.error.connect(lambda x: QMessageBox().information(None, "Загрузка информации с сервера",
                                                                       x.message))
        result = self.manager.post(self.request, data)


def BisitorRequest(address, user, data, on_finish=None, on_error=None):
    from urllib.request import Request, urlopen

    data = pack(user, data)
    address = get_full_address(address)
    print(f'request {address}')
    request = Request(
        address,
        bytes(JsonParser.dump(data), encoding='utf8'),
        headers={'Content-Type': 'application/json"'})
    res = urlopen(request).read().decode()

    return res
