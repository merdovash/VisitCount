from typing import List, Dict

from DataBase2 import DataView, Auth
from Modules.API import API
from Modules.UpdateDataViews import DataViewsResponse
from Server import Response


class DataViewAPI(API):
    __address__ = API.__address__ + '/data_view'

    def __init__(self, app, request):
        super().__init__(app, request, self.__address__)

    @classmethod
    def load(cls, user, on_finish, on_error):
        def apply(data: List[Dict]):
            for view in data:
                if isinstance(view, dict):
                    view = DataView.get_or_create(**view, session=user.session())
            user.session().commit()

            on_finish()

        from Client.MyQt.Widgets.Network.BisitorRequest import QBisitorRequest
        manager = QBisitorRequest(
            '/data_views',
            user,
            {},
            apply,
            on_error)

        return manager

    def post(self, data: dict, auth: Auth, **kwargs):
        views = DataView.all()
        return views
