from typing import Dict, List

from Client.Requests.ClientConnection import ServerConnection
from DataBase.Authentication import Authentication
from DataBase.sql_handler import ClientDataBase
from Modules.Synchronize import address


class Synchronize(ServerConnection):
    def __init__(self, program: 'MyProgram', db: ClientDataBase, auth: Authentication):
        super().__init__(db, auth, program['host']+address)
        self.db: ClientDataBase = db
        self.professor = self._get_professor(auth.user_id)

    def _run(self):
        self.send({"type": "synch",
                   "user": {
                       "login": self.professor[0],
                       "password": self.professor[1]
                   }})

    def on_response(self, data: Dict[str, List[Dict[str, str or int]]]):
        for table in data.keys():
            if table == self.db.config.students:
                for student in data[table]:
                    self.db.update_student(**student)
