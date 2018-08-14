import json
from threading import Thread

import requests
from PyQt5.QtWidgets import QLabel

from Client import config
from Client.MyQt.Window.Chart.QAnalysisDialog import QAnalysisDialog
from Client.Types import Status, Response, WorkingData


class BisitorRequest:
    def __init__(self,
                 req_type: str = "null",
                 data: dict = None,
                 on_response: callable = lambda x: 0,
                 on_error: callable(dict) = lambda x: 0):
        self.req_type = req_type
        self.data = data
        self.on_response = on_response
        self.on_error = on_error

        Thread(target=self._start).start()

    def _start(self):
        try:
            r = requests.post(
                url=config.server,
                headers={"Content-Type": "application/json"},
                data=json.dumps({"type": self.req_type,
                                 "data": self.data})
            )

            res_status = Status(r.text)
            if res_status == Response.JSON:
                res = json.loads(r.text)
                if res["type"] == "first":
                    if res["status"] == "OK":
                        self.on_response(res["data"])
                else:
                    self.on_error(-2)
            elif res_status == Response.ERROR:
                self.on_error(r.status_code)
                print("запрос неудачный. код ошибки: ", r.status_code)

        except requests.exceptions.ConnectionError as e:
            self.on_error(-1)
            print("No internet connection to Server")


class Statistic:
    # TODO loading from server
    loaded = {}

    @staticmethod
    def load(data_type: QAnalysisDialog.DataType):
        if data_type not in Statistic.loaded.keys():
            Statistic._load(data_type)
        else:
            return Statistic.loaded[data_type]

    @staticmethod
    def _load(data_type: QAnalysisDialog.DataType):
        BisitorRequest(
            req_type="statistic",
            data={"card_id": WorkingData.instance().professor["card_id"],
                  "password": WorkingData.instance().professor["password"],
                  "statistic_type": data_type},
            on_response=Statistic._save())

    @staticmethod
    def _save(data_type: QAnalysisDialog.DataType):
        def __save(res: dict):
            Statistic.loaded[data_type] = res

        return __save
