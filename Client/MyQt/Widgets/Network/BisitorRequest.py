from PyQt5.QtCore import QUrl, pyqtSignal
from PyQt5.QtNetwork import QNetworkRequest, QNetworkAccessManager, QNetworkReply
from PyQt5.QtWidgets import QMessageBox

from Parser.JsonParser import JsonParser
from Server.Response import Response


class QBisitorRequest(QNetworkRequest):
    def __init__(self, *__args):
        url = __args[0]
        if isinstance(url, str):
            url = QUrl(url)
        super().__init__(url, *__args[1:])
        self.setHeader(QNetworkRequest.ContentTypeHeader, "application/json")


class QBisitorAccessManager(QNetworkAccessManager):
    response = pyqtSignal('PyQt_PyObject')

    def __init__(self, professor):
        super().__init__()

        self.data = {
            'user': professor.auth.data()
        }

        self.finished.connect(self.on_finish)

    def post(self, request: QNetworkRequest, data=None, *__args):
        self.data['data'] = data
        print('request', request.url())
        return super().post(request, bytearray(JsonParser.dump(self.data), encoding='utf-8'), *__args)

    def on_finish(self, reply: QNetworkReply):
        if reply.error() == QNetworkReply.NoError:
            bytes_string = reply.readAll()
            response = Response.load(**JsonParser.read(str(bytes_string, 'utf-8')))
            if response.status == response.Status.OK:
                self.response.emit(response.data)
            else:
                QMessageBox().information(self, "Загрузка информации с сервера", response.message)
        else:
            QMessageBox().information(self, "Загрузка информации с сервера",
                                      f"Сервер не смог ответить на запрос.\n код ошибки: {str(reply.error())}")

        self.deleteLater()


def BisitorRequest(address, user, data, callback):
    manager = QBisitorAccessManager(user)
    request = QBisitorRequest(address)
    manager.response.connect(callback)
    manager.post(request, data)
    return manager
