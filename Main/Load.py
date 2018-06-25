import requests
import json

import Main.sql_handler as sql
from Main import config


class FirstLoad:
    def __init__(self, password, card_id, db: sql.DataBaseWorker):
        self.address = 'http://schekochikhin.pythonanywhere.com/'
        self.password = password
        self.card_id = card_id

        self.db = db

    def run(self):
        r = requests.post(
            url=self.address,
            headers={"Content-Type": "application/json"},
            data=json.dumps({'type': 'first',
                             'card_id': self.card_id,
                             'password': self.password}
                            ))

        print(r.text)
        res = json.loads(r.text)
        print(res)

        if res["type"] == "first":
            if res["status"] == "OK":
                data = res["data"]
                db_res = self.db.loads(config.students, data["students"])
                print(db_res)
                return True
            else:
                return False
        else:
            return False


class SendNewVisitation:
    def __init__(self, db:sql.DataBaseWorker):
        self.db = db

    def run(self):
        self.db.get_visitations(synch=0)

if __name__ == "__main__":
    f = FirstLoad(card_id="61157", password="123456", db=sql.DataBaseWorker())
    f.run()
