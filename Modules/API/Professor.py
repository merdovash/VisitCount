from Client.MyQt.Widgets.Network.BisitorRequest import BisitorRequest
from Client.MyQt.utils import check_connection
from DataBase2 import Professor, Auth
from Modules.API import API
from Parser import Args
from Server.Response import Response


class ProfessorApi(API):
    address = API.address + '/professor'

    def __init__(self, app, request):
        super().__init__(app, request, '/professor')


class ProfessorSettingsApi(ProfessorApi):
    address = ProfessorApi.address + '/settings'

    @classmethod
    def synch_settings(cls, professor: Professor):
        if check_connection():
            if professor.has_local_updates():
                def on_finish(result):
                    professor.settings = result

                BisitorRequest(
                    Args().host + cls.address,
                    professor,
                    data=professor.settings,
                    on_finish=on_finish
                )

    def post(self, data: dict, response: Response, auth: Auth, **kwargs):
        print(data)