from Parser.JsonParser import jsonParser


class Response:
    def __init__(self, type):
        self.type = type

    def set_data(self, data):
        self.status = "OK"
        self.data = data
        return self

    def set_error(self, msg):
        self.status = "ERROR"
        self.message = msg
        return self

    def __call__(self, *args, **kwargs):
        return jsonParser.dump(self.__dict__)
