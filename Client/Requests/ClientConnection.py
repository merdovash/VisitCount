"""
This module contains Abstract class of post request.

You need to override class ServerConnection and override methods _run, on_response and on_error
"""

from threading import Thread

import requests
from requests import post

from Client.Types import Status, Response
from Client.test import safe
from DataBase.Authentication import Authentication
from DataBase.ClentDataBase import ClientDataBase
from DataBase.Types import cached
from Parser.JsonParser import JsonParser


class ServerConnection(Thread):
    """
    Abstract class wrapper of post request
    """

    @safe
    def __init__(self, database: ClientDataBase, auth: Authentication, url: str):
        super().__init__(target=self._run)
        self.database: ClientDataBase = database
        self.auth = auth
        self.url = url

    @cached
    def _get_professor(self, professor_id):
        return [{'login': i[0], 'password': i[1]} for i in self.database.sql_request(f"""
        SELECT login, password 
        FROM {self.database.config.auth} 
        WHERE user_id={professor_id} AND user_type=1;""")][0]

    @safe
    def _send(self, data: dict):
        try:

            request = post(url=self.url,
                           headers={"Content-Type": "application/json"},
                           data=JsonParser.dump(data))

            res_status = Status(request.text)
            # print(r.text)
            if res_status == Response.JSON:
                res = JsonParser.read(request.text)
                if res["status"] == "OK":
                    self.on_response(res["data"])
                else:
                    self.on_error(f"Неудачная удаленная аутентификациия: {res['message']}")
            else:
                self.on_error(str(request.status_code) + '<br>' + str(request.text))
        except requests.exceptions.ConnectionError as connection_error:
            self.on_error(f"""Отсутсвует возможность аутентификации так как: <br>
                1. Не удалось аутентифицировать локально (возможно неверно введен логин или пароль) <br>
                2. Удаленный сервер недоступен <br> <br> 
                Ошибка: {str(connection_error)}""")

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
