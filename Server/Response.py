import json


def json_create(val):
    """

    :param val: object
    :return: encoded json string
    """

    def encode(v) -> str:
        # TODO: сделать кодировку
        """

        :param v: string
        :return: encoded string
        """
        return v

    return json.dumps(encode(val)).encode("utf-8")


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
        return json_create(self.__dict__)
