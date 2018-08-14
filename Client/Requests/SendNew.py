from Client.Requests.Server import Server
from DataBase.Authentication import Authentication
from DataBase.sql_handler import ClientDataBase


class SendNewVisitation(Server):
    def __init__(self, db: ClientDataBase, auth: Authentication):
        super().__init__(db, auth)
        self.professor = self._get_professor(auth.get_user_info()['id'])
        self.visits = self.db.get_visitations(synch=0)

    def _run(self):
        self.send(request="/new_visits",
                  data={"type": "new_visits",
                        "data": {
                            "login": self.professor['login'],
                            'password':self.professor['password'],
                            'visits':self.visits
                        }},
                  onResponse=self.on_response,
                  onError=self.on_error)

    def on_response(self, data):
        if data['count']==len(self.visits):
            # TODO: commit synchronized visitations
            pass


