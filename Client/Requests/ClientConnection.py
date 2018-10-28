"""
This module contains Abstract class of post request.

You need to override class ServerConnection and override methods _run, on_response and on_error
"""

from threading import Thread

import requests
from requests import post

from Client.IProgram import IProgram
from Client.Types import Status, Response
from Client.test import safe
from DataBase2 import Auth
from Exception import NoSuchUserException
from Parser.JsonParser import JsonParser


class ServerConnection(Thread):
    """
    Abstract class wrapper of post request
    """

    def __init__(self, auth: Auth, url: str, program: IProgram):
        super().__init__(target=self.run)
        self.auth = None
        self.login = auth.login
        self.password = auth.password
        self.url = program.host + url

    # cached
    def get_user(self):
        return self.auth.user

    def get_auth(self):
        return self.auth

    def _send(self, data: dict):
        try:

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
        try:
            self.auth = Auth.log_in(self.login, self.password)
        except NoSuchUserException:
            self.auth = Auth(self.login, self.password)
        self._run()

    @safe
    def _run(self):
        raise NotImplementedError()

    @safe
    def on_response(self, data):
        """
        abstract method
        :param data:
        """
        raise NotImplementedError()

    @safe
    def on_error(self, msg):
        """
        abstract method
        :param msg:
        """
        raise NotImplementedError()
