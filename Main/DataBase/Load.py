import json
import time
from threading import Thread

import requests
from PyQt5.QtWidgets import QWidget, QLabel, QDialog

from Main import config
from Main.DataBase.sql_handler import DataBaseWorker
from Main.MyQt.Dialogs.ServerNotResponse import Server504
from Main.MyQt.QtMyDownloadingWidget import QLoadingWidget
from Main.Types import LoadingInfo, Status, Response


class FirstLoad:
    class AuthType(int):
        ByLogin = 0
        ByCard = 1

    def __init__(self, login=None, card_id=None, password=None, parent: QWidget = None, on_finish: callable = None):
        self.address = config.server
        self.password = password
        if card_id is not None:
            self.auth_type = FirstLoad.AuthType.ByCard
            self.card_id = card_id
        elif login is not None:
            self.auth_type = FirstLoad.AuthType.ByLogin
            self.login = login
        else:
            raise Exception("expected card_id or login parameter")

        self.parent = parent
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

        def a():
            """
            updating loading info

            :return: None
            """
            try:
                while True:
                    if type(self.parent.loading_info) == QLoadingWidget:
                        self.parent.loading_info.update(self.marker)
                    time.sleep(0.001)
            except Exception as e:
                print("ERROR: FIRSTLOAD-> marker function->", e)

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
                            self.parent.loading_info = QLoadingWidget()
                            self.parent.inner_layout.addWidget(self.parent.loading_info)

                            # handle data
                            data = res["data"]
                            for table in [config.professors,
                                          config.students,
                                          config.groups,
                                          config.students_groups,
                                          config.disciplines,
                                          config.lessons,
                                          config.visitation,
                                          config.auth]:
                                DataBaseWorker.instance().loads(table, data[table], self.marker)

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
                print("No internet connection to Server")

        Thread(target=a).start()
        Thread(target=b).start()


class SendNewVisitation:
    def __init__(self):
        self.db = DataBaseWorker.instance()

    def run(self):
        self.db.get_visitations(synch=0)


if __name__ == "__main__":
    f = FirstLoad(card_id="61157", password="123456")
    f.run()
