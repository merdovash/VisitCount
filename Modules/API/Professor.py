from datetime import datetime

import requests

from Client.MyQt.Widgets.Network.BisitorRequest import QBisitorRequest, BisitorRequest
from Client.MyQt.utils import check_connection
from DataBase2 import Professor, Auth
from Modules.API import API
from Parser import Args
from Parser.JsonParser import JsonParser
from Server.Response import Response


class ProfessorApi(API):
    address = API.address + '/professor'


class ProfessorSettingsApi(ProfessorApi):
    """
    Протокол синхронизации параметров отображения таблицы посещений

    Отправляет данные о последнем обновлении настроек и сами настройки

    Получает один из следующих вариантов:
        1) {msg: OK} если локальные настройки были записаны на сервер
        2) {settings: <dict>} если серверные настройки "свежее" - значет необходимо их применить локально

    """

    address = ProfessorApi.address + '/settings'

    @classmethod
    def synch(cls, professor: Professor):
        if check_connection():
            if professor.has_local_updates(professor._last_update_in):
                def on_finish(result):
                    result = JsonParser.read(result)
                    result_data = result['data']
                    if 'settings' in result_data:
                        professor.settings = result_data['settings']

                result = BisitorRequest(
                    Args().host + cls.address,
                    professor,
                    data={
                        'settings': professor.settings,
                        'last_update': professor.last_update()
                    }

                )

                on_finish(result)

    def post(self, data: dict, response: Response, auth: Auth, **kwargs):
        """

        :param data: {
            'settings': dict,
            'last_update': datetime
        }
        :param response:
        :param auth:
        :param kwargs:
        :return:
        """
        user = auth.user
        if not isinstance(user, Professor):
            response.set_error("Только для преподавателей")

        professor = user
        if data['settings'] != professor.settings:
            if professor.settings is None:
                professor.settings = data['settings']
                professor.session().commit()

                response.set_data({
                    'msg': 'OK'
                })
            else:
                if professor.has_local_updates(data['last_update']):
                    response.set_data({
                        'settings': professor.settings
                    })
                else:
                    professor.settings = data['settings']
                    professor.session().commit()

                    response.set_data({
                        'msg': 'OK'
                    })