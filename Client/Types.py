import json


class LoadingInfo:
    """
    class descibes downloading status
    """

    def __init__(self):
        self.inserted = 0
        self.total = 0
        self.table = ""


class Response(int):
    """
    Response statuses for server
    """
    JSON = 1
    ERROR = 0


def Status(res) -> int:
    try:
        json.loads(res)
        return Response.JSON
    except json.decoder.JSONDecodeError:
        return Response.ERROR

