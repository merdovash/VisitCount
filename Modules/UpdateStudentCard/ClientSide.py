from typing import List, Dict

from Client.Requests.ClientConnection import ServerConnection
from DataBase import Authentication
from DataBase.sql_handler import ClientDataBase

from Modules.UpdateStudentCard import address


class UpdateStudentCard(ServerConnection):
    def __init__(self, program: 'MyProgram', db: ClientDataBase, auth: Authentication,
                 students: List[Dict[str, str or int]]):
        super().__init__(db, auth, program['host'] + address)
        self.students = students

    def _run(self):
        self.send(data={
            'user': {
                'login': self.auth.get_user_info()['login'],
                'password': self.auth.get_user_info()['password']
            },
            'data': self.students
        })

    def on_error(self, msg):
        # TODO in case of error mark students to be updated later
        pass
