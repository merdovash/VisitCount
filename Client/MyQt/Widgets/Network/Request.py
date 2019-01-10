import json
import sys
from typing import Dict, Callable

from PyQt5.QtCore import QUrl
from PyQt5.QtNetwork import QNetworkAccessManager, QNetworkReply, QNetworkRequest
from PyQt5.QtWidgets import QWidget, QHBoxLayout, QPushButton, QVBoxLayout, QLabel, QApplication

from Client.MyQt.Widgets.ProgressBar import ProgressBar
from DataBase2 import Professor, Auth, UserType
from Domain.Structures.DictWrapper import Structure
from Domain.Structures.DictWrapper.Network.FirstLoad import ClientFirstLoadData
from Domain.Structures.DictWrapper.Network.Synch import ClientUpdateData
from Modules.FirstLoad.ClientSide import ApplyFirstLoadData
from Modules.Synch.ClientSide import ApplyUpdate
from Parser.JsonParser import JsonParser


class RequestWidget(QWidget):
    def __init__(self, professor: Professor or None, data: Dict or Structure, address: str,
                 on_response: Callable[[Dict, ProgressBar], None],
                 on_finish: Callable,
                 on_error: Callable[[int], None],
                 flags=None, text_button: str = 'Запустить', title: str = '%Запрос на сервер%', *args, **kwargs):
        super().__init__(flags, *args, **kwargs)

        self.manager = QNetworkAccessManager(self)
        self.manager.finished.connect(self._on_finish)

        self.address = address

        self.on_response = on_response
        self.on_finish = on_finish
        self.on_error = on_error

        self.data = data

        self.professor = professor

        layout = QVBoxLayout()

        self.title = QLabel()
        self.title.setText(title)
        layout.addWidget(self.title)

        inner_layout = QHBoxLayout()
        self.button = QPushButton()
        self.button.setText(text_button)
        self.button.clicked.connect(self._run_once)
        inner_layout.addWidget(self.button)

        self.progress_bar = ProgressBar(self)
        inner_layout.addWidget(self.progress_bar)

        layout.addLayout(inner_layout)

        self.setLayout(layout)

    def _on_finish(self, reply: QNetworkReply):
        self.progress_bar.set_part(10, 1, 'Чтение ответа')
        error_code = reply.error()

        if error_code == QNetworkReply.NoError:
            bytes_string = reply.readAll()

            json_ar = json.loads(str(bytes_string, 'utf-8'))
            print(json_ar)
            if json_ar['status']=='OK':
                self.progress_bar.increment()
                self.on_response(json_ar['data'], self.progress_bar)
                self.progress_bar.on_finish('Успешно синхронизированно', self.on_finish)
            else:
                self.progress_bar.abord()
                self.button.setEnabled(True)
                self.on_error(str(error_code))
                self.progress_bar.on_finish(f'Завершено с ошибкой {json_ar["message"]}', self.on_finish)
        else:
            print(error_code)
            self.progress_bar.abord()
            self.button.setEnabled(True)
            self.on_error(error_code)
            self.progress_bar.on_finish(f'Завершено с ошибкой {error_code}', self.on_finish)

    def _run_once(self):
        self.progress_bar.set_part(25, 1, 'Отправка сообщения')

        if self.professor is not None:
            auth = Auth.get(self.professor.session, user_id=self.professor.id, user_type=UserType.PROFESSOR)
            data = {
                'user': {
                    'login': auth.login,
                    'password': auth.password},
                'data': self.data
            }
        else:
            data = {
                'user': {
                    'login': self.data.login,
                    'password': self.data.password
                }
            }
        self.request = QNetworkRequest(QUrl(self.address))
        self.request.setHeader(QNetworkRequest.ContentTypeHeader, "application/json")
        self.manager.post(self.request, bytearray(JsonParser.dump(data), encoding='utf8'))
        self.progress_bar.increment()
        self.button.setEnabled(False)


def send_updates(program):
    from Modules.Synch import address

    professor = program.professor
    widget = RequestWidget(
        professor=professor,
        data=ClientUpdateData(
            updates=professor.updates(),
            last_update_in=professor._last_update_in,
            last_update_out=professor._last_update_out),
        address=program.host + address,
        on_response=ApplyUpdate(program.professor),
        on_error=lambda x: None,
        on_finish=lambda x: None
    )
    widget.on_finish = widget.close

    return widget


def first_load(program, login, password, on_finish, on_error):
    from Modules.FirstLoad import address

    return RequestWidget(
        professor=None,
        data=ClientFirstLoadData(login=login, password=password),
        address=program.host+address,
        text_button="Загрузить данные",
        title="Данные отсутствуют",
        on_response=ApplyFirstLoadData(),
        on_error=on_error,
        on_finish=on_finish
    )


if __name__ == '__main__':
    app = QApplication(sys.argv)

    widget = RequestWidget(Auth.log_in('VAE', '123456').user, {'1': '2'}, 'http://127.0.0.1:5000/first_load',
                           on_response=print, on_error=print)
    widget.show()

    sys.exit(app.exec_())
