import json
import threading

import requests

from DataBase.sql_handler import DataBaseWorker
from Main import config
from Main.MyQt.QtMyStatusBar import QStatusMessage
from Main.Types import Status, Response


def finish_synch(db: DataBaseWorker, visitations: list):
    for i in visitations:
        db.sql_request("UPDATE {} SET synch=1 WHERE student_id={} AND id={}",
                       config.visitation,
                       i["student_id"],
                       i["id"])


def send(db: DataBaseWorker, professor_id: int):
    def a():
        visitations = db.get_visitations(synch=0)
        user = db.get_auth(professor_id=professor_id)[0]

        try:
            r = requests.post(url=config.server,
                              headers={"Content-Type": "application/json"},
                              data=json.dumps({"type": "synch",
                                               "card_id": user["card_id"],
                                               "password": user["password"],
                                               "data": visitations})
                              )

            status = Status(r.text)
            if status == Response.JSON:
                res = json.loads(r.text)
                if res["type"] == "synch":
                    if res["status"] == "OK":
                        print("synch success")
                        finish_synch(db, visitations)
                        QStatusMessage.instance().setText("Сервер записал изменения")
                    elif res["status"] == "ERROR":
                        print(res["message"])
                        QStatusMessage.instance().setText("Сервер не записал изменения. Код ошибки: {}".format(
                            res["message"])
                        )
                    else:
                        print("something wrong")
                        QStatusMessage.instance().setText("Сервер не записал изменения с неизвестной ошибкой")
                else:
                    print("request type", res["status"])
            else:
                print("response type", r.text)
                QStatusMessage.instance().setText("Ответ сервера неверный")
        except requests.exceptions.ConnectionError as e:
            print("No internet connection to server")

    t = threading.Thread(target=a)
    t.start()
