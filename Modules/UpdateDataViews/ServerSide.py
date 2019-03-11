from DataBase2 import DataView
from Modules.UpdateDataViews import address, DataViewsResponse
from Server.Response import Response


def init(app, request):
    @app.route(address, methods=['POST'])
    def get_data_views():
        views = DataView.all()
        response = Response(address[1:])
        response.set_data(DataViewsResponse(views), DataViewsResponse)
        return response()
