import json

from PyQt5.QtCore import QUrl, pyqtSignal, pyqtSlot, Qt
from PyQt5.QtNetwork import QNetworkAccessManager, QNetworkReply, QNetworkRequest
from PyQt5.QtWidgets import QWidget, QHBoxLayout, QPushButton, QVBoxLayout, QLabel, QMessageBox

from Client.MyQt.Widgets.ProgressBar import ProgressBar
from Modules.Client import ClientWorker
from Modules.FirstLoad.ClientSide import InitialDataLoader
from Parser.JsonParser import JsonParser


def nothing(*args, **kwargs):
    pass



class Requset_Ui:
    @staticmethod
    def setupUi(self: QWidget, **kwargs):
        self.setWindowModality(Qt.ApplicationModal)

        layout = QVBoxLayout()
        self.title = QLabel()
        self.title.setText(kwargs.get('title', '%Запрос на сервер%'))

        layout.addWidget(self.title)

        inner_layout = QHBoxLayout()
        self.button = QPushButton()
        self.button.setText(kwargs.get('text_button', 'Запустить'))

        inner_layout.addWidget(self.button)

        self.progress_bar = ProgressBar(self)

        inner_layout.addWidget(self.progress_bar)

        layout.addLayout(inner_layout)

        self.setLayout(layout)


class RequestWidget(QWidget, Requset_Ui):
    """
    Виджет выполнения запроса на сервер
    """
    send = pyqtSignal()
    read_response = pyqtSignal('PyQt_PyObject', 'PyQt_PyObject')
    finish = pyqtSignal('PyQt_PyObject')
    exit = pyqtSignal(bool)
    error = pyqtSignal('PyQt_PyObject')

    def on_error(self, error):
        QMessageBox().critical(self, "Ошибка", str(error))

    def __init__(self, worker: ClientWorker, parent=None, *args, **kwargs):
        QWidget.__init__(self, parent)
        Requset_Ui.setupUi(self, **kwargs)

        self.manager = QNetworkAccessManager(self)

        self.worker = worker

        self.button.clicked.connect(self.send)
        self.send.connect(self.on_run)
        self.manager.finished.connect(self.on_response)
        self.read_response.connect(self.worker.on_response)
        self.worker.finish.connect(self.finish)
        self.progress_bar.finish.connect(self.exit)
        self.progress_bar.finish.connect(self.close)
        self.error.connect(self.on_error)

    @pyqtSlot(QNetworkReply, name='on_response')
    def on_response(self, reply: QNetworkReply):
        self.progress_bar.set_part(10, 1, 'Чтение ответа')
        error_code = reply.error()

        if error_code == QNetworkReply.NoError:
            bytes_string = reply.readAll()

            json_ar = json.loads(str(bytes_string, 'utf-8'))
            print(json_ar)
            if json_ar['status'] == 'OK':
                self.progress_bar.increment()
                self.read_response.emit(json_ar['data'], self.progress_bar)
                self.finish.emit(json_ar['data'])
                self.progress_bar.on_finish('Успешно синхронизированно')
            else:
                self.progress_bar.abord()
                self.button.setEnabled(True)
                self.error.emit(str(error_code))
                self.progress_bar.on_finish(f'Завершено с ошибкой {json_ar["message"]}')
        else:
            print(error_code)
            self.progress_bar.abord()
            self.button.setEnabled(True)
            self.error.emit(error_code)
            self.progress_bar.on_finish(f'Завершено с ошибкой {error_code}')

    @pyqtSlot(name='on_run')
    def on_run(self, *args):
        self.progress_bar.set_part(25, 1, 'Отправка сообщения')

        self.request = QNetworkRequest(QUrl(self.worker.address))
        self.request.setHeader(QNetworkRequest.ContentTypeHeader, "application/json")
        self.manager.post(self.request, bytearray(JsonParser.dump(self.worker.data), encoding='utf8'))
        self.progress_bar.increment()
        self.button.setEnabled(False)
