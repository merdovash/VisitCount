"""
This module contains Abstract class of post request.

You need to override class ServerConnection and override methods _run, on_response and on_error
"""

from threading import Thread

import requests
from requests import post

from Client.Types import Status, Response
from Parser.JsonParser import JsonParser


class ServerConnection(Thread):
    """
    Abstract class wrapper of post request
    """

    UserBlock = 'user'

    def __init__(self, login, password, url, **kwargs):
        super().__init__(target=self.run)
        self.auth = None
        self.login = login
        self.password = password
        self.url = url

        self.on_error = kwargs.get("on_error", self.on_error)
        self.on_finish = kwargs.get("on_finish", self.on_finish)
        self.on_response = kwargs.get('on_response', self.on_response)

    def _send(self, data: dict):
        try:
            if ServerConnection.UserBlock not in data.keys():
                data[ServerConnection.UserBlock] = dict(login=self.login, password=self.password)

            request = post(url=self.url,
                           headers={"Content-Type": "application/json"},
                           data=JsonParser.dump(data).encode('utf-8'))

            res_status = Status(request.text)
            # print(r.text)
            if res_status == Response.JSON:
                res = JsonParser.read(request.text)
                if res["status"] == "OK":
                    self.on_response(res["data"])
                else:
                    self.on_error(f"Неудачная удаленная аутентификациия: {res}")
            else:
                self.on_error(str(request.status_code) + '<br>' + str(request.text))
        except requests.exceptions.ConnectionError as connection_error:
            self.on_error(f"""Отсутсвует возможность аутентификации так как: <br>
                1. Не удалось аутентифицировать локально (возможно неверно введен логин или пароль) <br>
                2. Удаленный сервер недоступен <br> <br> 
                Ошибка: {str(connection_error)}""")

    def run(self):
        self._run()

    @classmethod
    def _run(self):
        raise NotImplementedError()

    @classmethod
    def on_response(cls, data):
        """
        abstract method
        :param data:
        """
        raise NotImplementedError()

    @classmethod
    def on_error(cls, msg):
        """
        abstract method
        :param msg:
        """
        raise NotImplementedError()

    @classmethod
    def on_finish(cls):
        raise NotImplementedError()
