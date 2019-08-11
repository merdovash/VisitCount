from PyQt5.QtCore import QUrl, pyqtSignal
from PyQt5.QtNetwork import QNetworkRequest, QNetworkAccessManager, QNetworkReply
from PyQt5.QtWidgets import QMessageBox

from Parser import Args
from Parser.JsonParser import JsonParser
from Server.Response import Response


def pack(user, data):
    return dict(user=user.auth.data(), data=data)


class _QBisitorRequest(QNetworkRequest):
    def __init__(self, *__args):
        url = __args[0]
        if isinstance(url, str):
            url = QUrl(url)
        super().__init__(url, *__args[1:])
        self.setHeader(QNetworkRequest.ContentTypeHeader, "application/json")


class QBisitorAccessManager(QNetworkAccessManager):
    response = pyqtSignal('PyQt_PyObject')
    error = pyqtSignal('PyQt_PyObject')

    def __init__(self, professor, response_type):
        super().__init__()

        if professor is not None:
            self.data = {
                'user': professor.auth.data()
            }
        else:
            self.data = {}
        self.response_type = response_type
        self.finished.connect(self.on_finish)

    def post(self, request: QNetworkRequest, data=None, *__args):
        self.data['data'] = data
        print('request', request.url())
        return super().post(request, bytearray(JsonParser.dump(self.data), encoding='utf-8'), *__args)

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

    def __init__(self, address, user, data, on_finish, on_error=None, response_type=None):
        host = Args().host
        if host[:4] != 'http':
            host = 'http://' + host
        if host not in address:
            url = host + address
        else:
            url = address

        manager = QBisitorAccessManager(user, response_type if response_type is not None else self.response_type)
        request = _QBisitorRequest(url)
        manager.response.connect(on_finish)
        if on_error is not None:
            manager.error.connect(on_error)
        else:
            manager.error.connect(lambda x: QMessageBox().information(None, "Загрузка информации с сервера", x.message))
        result = manager.post(request, data)


def BisitorRequest(address, user, data, on_finish=None, on_error=None):
    from urllib.request import Request, urlopen

    data = pack(user, data)
    print(bytes(JsonParser.dump(data), encoding='utf8'))
    request = Request(
        address,
        bytes(JsonParser.dump(data), encoding='utf8'),
        headers={'Content-Type': 'application/json"'})
    res = urlopen(request).read().decode()

    return res
