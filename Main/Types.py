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


class WorkingData:
    inst = None

    @staticmethod
    def instance():
        if WorkingData.inst is None:
            WorkingData.inst = WorkingData()
        return WorkingData.inst

    def __init__(self):
        self.professor = None
        self.group = None
        self.discipline = None
        self.lesson = None
        self.marking_visits = False
