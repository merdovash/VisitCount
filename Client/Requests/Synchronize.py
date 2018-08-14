from typing import Dict, List

from Client.Requests.Server import Server
from DataBase.Authentication import Authentication
from DataBase.sql_handler import ClientDataBase
from config2 import DataBaseConfig


class Synchronize(Server):
    def __init__(self, db: ClientDataBase, professor_id, auth: Authentication):
        super().__init__(db, auth)
        self.db: ClientDataBase = db
        self.professor = self._get_professor(professor_id)

    def _run(self):
        self.send(request="/synchronize",
                  data={"type": "synch",
                        "data": {
                            "login": self.professor[0],
                            "password": self.professor[1]
                        }},
                  onResponse=self.on_response,
                  onError=self.on_error)

    def on_response(self, data: Dict[str, List[Dict[str, str or int]]]):
        print("synch OK")
        for table in data.keys():
            if table == self.db.config.students:
                for student in data[table]:
                    self.db.update_student(**student)


if __name__=="__main__":
    db = ClientDataBase(DataBaseConfig())
    Synchronize(db=db, professor_id=1, auth=Authentication(db, login='VAE', password='123456')).run()
