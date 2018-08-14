import json
from threading import Thread

import requests
from requests import post

from Client.Types import Status, Response
from Client.test import try_except
from DataBase.Authentication import Authentication
from DataBase.sql_handler import ClientDataBase


class Server(Thread):
    def __init__(self, db: ClientDataBase, auth: Authentication):
        super().__init__(target=self._run)
        self.db: ClientDataBase = db
        self.auth = auth

    def _get_professor(self, professor_id):
        return self.db.sql_request(f"""
        SELECT login, password 
        FROM {self.db.config.auth} 
        WHERE user_id={professor_id} AND user_type=1;""")[0]

    @try_except
    def send(self, request: str, data: dict, onResponse: callable = lambda x: 0, onError: callable = lambda x: 0):
        try:
            r = post(url=self.db.config.server + request,
                     headers={"Content-Type": "application/json"},
                     data=json.dumps(data))

            res_status = Status(r.text)
            if res_status == Response.JSON:
                res = json.loads(r.text)
                if res["type"] == data["type"]:
                    if res["status"] == "OK":
                        onResponse(res["data"])
                    else:
                        onError(res["message"])
                else:
                    onError(res["message"])
            else:
                onError(r.status_code)
        except requests.exceptions.ConnectionError:
            onError("no connection")

    def _run(self):
        pass

    def on_response(self, data):
        pass

    def on_error(self, msg):
        pass

