from threading import Thread

import requests
from requests import post

from Client.Types import Status, Response
from Client.test import safe
from DataBase.Authentication import Authentication
from DataBase.Types import cached
from DataBase.sql_handler import ClientDataBase
from Parser.JsonParser import JsonParser


class ServerConnection(Thread):
    def __init__(self, db: ClientDataBase, auth: Authentication, url: str):
        super().__init__(target=self._run)
        self.db: ClientDataBase = db
        self.auth = auth
        self.url = url

    @cached
    def _get_professor(self, professor_id):
        return [{'login': i[0], 'password': i[1]} for i in self.db.sql_request(f"""
        SELECT login, password 
        FROM {self.db.config.auth} 
        WHERE user_id={professor_id} AND user_type=1;""")][0]

    @safe
    def send(self, data: dict):
        try:

            r = post(url=self.url,
                     headers={"Content-Type": "application/json"},
                     data=JsonParser.dump(data))

            res_status = Status(r.text)
            # print(r.text)
            if res_status == Response.JSON:
                res = JsonParser.read(r.text)
                if res["status"] == "OK":
                    self.on_response(res["data"])
                else:
                    self.on_error(f"Неудачная удаленная аутентификациия: {res['message']}")
            else:
                self.on_error(str(r.status_code) + '<br>' + str(r.text))
        except requests.exceptions.ConnectionError as e:
            self.on_error(f"""Отсутсвует возможность аутентификации так как: <br>
                1. Не удалось аутентифицировать локально (возможно неверно введен логин или пароль) <br>
                2. Удаленный сервер недоступен <br> <br> 
                Ошибка: {str(e)}""")

    def _run(self):
        pass

    def on_response(self, data):
        pass

    def on_error(self, msg):
        pass
