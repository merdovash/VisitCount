from Client.Requests.ClientConnection import ServerConnection
from DataBase.Authentication import Authentication
from DataBase.sql_handler import ClientDataBase
from Modules.NewVisits import address


class SendNewVisitation(ServerConnection):
    def __init__(self, program: 'MyProgram', db: ClientDataBase, auth: Authentication):
        super().__init__(db, auth, program['host'] + address)
        self.professor = self._get_professor(auth.get_user_info()['id'])
        self.visits = self.db.get_visitations(synch=0)

    def _run(self):
        self.send({"type": "new_visits",
                   "user": {
                       "login": self.professor['login'],
                       'password': self.professor['password'],
                   },
                   'data': {
                       'visits': self.visits
                   }
                   })

    def on_response(self, data):
        if data['count'] == len(self.visits):
            for visit in self.visits:
                self.db.sql_request('update {0} set completed=1 WHERE lesson_id={} AND student_id={}',
                                    self.db.config.visitation,
                                    visit['lesson_id'],
                                    visit['student_id'])

