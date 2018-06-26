import threading
from threading import Thread

import requests
import json

import time

import Main.sql_handler as sql
from Main import config


class FirstLoad:
    def __init__(self,
                 password,
                 card_id,
                 db: sql.DataBaseWorker,
                 data_totals: callable = None,
                 data_placer: callable = None,
                 on_finish: callable = None):
        self.address = config.server
        self.password = password
        self.card_id = card_id

        self.data_totals = data_totals
        self.data_placer = data_placer
        self.finish = on_finish
        self.db = db

        self.marker = {"inserted": "",
                       "total": "",
                       "table": ""}

    def run(self):

        def a():
            try:
                while True:
                    self.data_placer(self.marker)
                    time.sleep(1)
            except Exception as e:
                print("ERROR: FIRSTLOAD-> marker function->", e)

        def b():

            r = requests.post(
                url=self.address,
                headers={"Content-Type": "application/json"},
                data=json.dumps({'type': 'first',
                                 'card_id': self.card_id,
                                 'password': self.password}
                                ))

            res = json.loads(r.text)
            if res["type"] == "first":
                if res["status"] == "OK":
                    data = res["data"]
                    self.data_totals(data)
                    for table in [config.professors, config.students, config.students_groups, config.disciplines,
                                  config.lessons, config.visitation]:
                        self.db.loads(table, data[table], self.marker)
                        self.data_placer({"inserted": len(data[table]),
                                          "table": table,
                                          "total": len(data[table])})
                    # self.data_totals(data)
                    # print("Загрузка преподавателей ({})".format(len(data["professor"])))
                    # self.db.loads(config.professors, data["professor"], self.marker)
                    # print("Загрузка гурпп({})".format(len(data["groups"])))
                    # self.db.loads(config.groups, data["groups"], self.marker)
                    # print("Загрузка студентов ({})".format(len(data["students"])))
                    # self.db.loads(config.students, data["students"], self.marker)
                    # print("Загрузка ассоциативной таблицы Студенты-Группы ({})".format(len(data["students_groups"])))
                    # self.db.loads(config.students_groups, data["students_groups"], self.marker)
                    # print("Загрузка занятий ({})".format(len(data["lessons"])))
                    # self.db.loads(config.lessons, data["lessons"], self.marker)
                    # print("Загрузка дисциплин ({})".format(len(data["disciplines"])))
                    # self.db.loads(config.disciplines, data["disciplines"], self.marker)
                    # print("Загрузка посещений ({})".format(len(data["visitations"])))
                    # self.db.loads(config.visitation, data["visitations"], self.marker)

                    self.finish()
            else:
                return False

        Thread(target=a).start()
        Thread(target=b).start()


class SendNewVisitation:
    def __init__(self, db: sql.DataBaseWorker):
        self.db = db

    def run(self):
        self.db.get_visitations(synch=0)


if __name__ == "__main__":
    f = FirstLoad(card_id="61157", password="123456", db=sql.DataBaseWorker())
    f.run()
