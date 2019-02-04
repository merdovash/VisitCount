"""
This module contains Abstract class of post request.

You need to override class ServerConnection and override methods _run, on_response and on_error
"""
import json
from threading import Thread
from urllib.parse import urlparse

import requests
from requests import post

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
        url_ = urlparse(url)
        self.host = url_.scheme+'://'+url_.netloc

        self.on_error = kwargs.get("on_error", self.on_error)
        self.on_finish = kwargs.get("on_finish", self.on_finish)
        self.on_response = kwargs.get('on_response', self.on_response)

    def _send(self, data: dict):
        try:
            client = requests.session()
            client.get(f"{self.host}/cabinet")

            if 'csrftoken' in client.cookies:
                # Django 1.6 and up
                csrftoken = client.cookies['csrftoken']
            else:
                # older versions
                csrftoken = client.cookies.get('csrf', None)

            if ServerConnection.UserBlock not in data.keys():
                data[ServerConnection.UserBlock] = dict(login=self.login, password=self.password)
            data['csrfmiddlewaretoken'] = csrftoken
            data['next'] = '/'

            request = post(url=self.url,
                           headers={"Content-Type": "application/json",
                                    "Referer": self.url},
                           data=self.dump_data(data))
            try:
                res = self.read_data(request.text)

                if res["status"] == "OK":
                    self.on_response(res["data"])
                else:
                    self.on_error(f"Неудачная удаленная аутентификациия: {res}")
            except json.decoder.JSONDecodeError:
                self.on_error(request.text)
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

    def dump_data(self, data):
        return JsonParser.dump(data).encode('utf-8')

    def read_data(self, data: str):
        return JsonParser.read(data)
