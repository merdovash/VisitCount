from Client.MyQt.Widgets.Network.BisitorRequest import QBisitorRequest
from Modules.UpdateDataViews import DataViewsResponse


def UpdateDataViews(user, on_finish, on_error):
    def apply(data: DataViewsResponse):
        print(data.views)
        user.session().commit()

        on_finish()

    manager = QBisitorRequest(
        '/data_views',
        user,
        {},
        apply,
        on_error)

    return manager
