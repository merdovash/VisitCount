import json
import time
from threading import Thread

import requests
from PyQt5.QtWidgets import QLabel

from DataBase.sql_handler import ClientDataBase

from Client.MyQt.Dialogs.ServerNotResponse import Server504
from Client.Types import LoadingInfo, Status, Response


class FirstLoad:
    class AuthType(int):
        ByLogin = 0
        ByCard = 1

    def __init__(self, db: ClientDataBase, login=None, card_id=None, password=None, parent: 'MyProgram' = None,
                 on_finish: callable = None):
        self.db = db
        self.address = self.db.server
        self.password = password
        if card_id is not None:
            self.auth_type = FirstLoad.AuthType.ByCard
            self.card_id = card_id
        elif login is not None:
            self.auth_type = FirstLoad.AuthType.ByLogin
            self.login = login
        else:
            raise Exception("expected card_id or login parameter")

        self.main = parent
        self.parent = parent.window.centralWidget()
        self.finish = on_finish

        self.marker = LoadingInfo()

    def get_request_body(self):
        if self.auth_type == FirstLoad.AuthType.ByLogin:
            return {'type': 'first',
                    'login': self.login,
                    'password': self.password}
        elif self.auth_type == FirstLoad.AuthType.ByCard:
            return {'type': 'first',
                    'card_id': self.card_id,
                    'password': self.password}

    def run(self):

        def b():
            """
            request function

            :return: None
            """
            try:
                r = requests.post(
                    url=self.address,
                    headers={"Content-Type": "application/json"},
                    data=json.dumps(self.get_request_body()))
                print(r.text)
                res_status = Status(r.text)
                if res_status == Response.JSON:
                    res = json.loads(r.text)
                    if res["type"] == "first":
                        if res["status"] == "OK":
                            # create and add Widget to display loading progress
                            self.parent.inner_layout.addWidget(self.parent.loading_info)

                            # handle data
                            data = res["data"]
                            config = self.db.config
                            for table in [config.professors,
                                          config.students,
                                          config.groups,
                                          config.students_groups,
                                          config.disciplines,
                                          config.lessons,
                                          config.visitation,
                                          config.auth]:
                                self.db.loads(table, data[table], self.marker)

                            self.parent.inner_layout.removeWidget(self.parent.loading_info)

                            self.finish()
                    else:
                        return False
                elif res_status == Response.ERROR:
                    if int(r.status_code) in [504]:
                        self.parent.showDialog(Server504(self.parent))
                    print("запрос неудачный. код ошибки: ", r.status_code)
                    if type(self.parent.loading_info) == QLabel:
                        self.parent.loading_info.setText(
                            "Запрос неудачный. " + str(r.status_code) + " " + str(r.reason))
                        # self.parent.inner_layout.removeWidget(self.parent.loading_info)
            except requests.exceptions.ConnectionError as e:
                self.main.window.error.emit("""Отсутсвует возможность аутентификации так как: <br>
                    1. Не удалось аутентифицировать локально (возможно неверно введен логин или пароль) <br>
                    2. Удаленный сервер недоступен <br>""" + str(e))
                # self.parent.message.show()

        Thread(target=b).start()


if __name__ == "__main__":
    f = FirstLoad(card_id="61157", password="123456")
    f.run()
