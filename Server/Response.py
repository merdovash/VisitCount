"""
response builder module
"""
from Parser.JsonParser import JsonParser


class Response(object):
    """
    main class of response builder
    """
    __slots__ = ('type', 'status', 'data', 'message', '_dumps')

    def __init__(self, response_type):
        self.type = response_type
        self.status = None
        self.data = None
        self.message = None
        self._dumps = lambda x: JsonParser.dump(x)

    def set_dumper(self, dumper: callable):
        self._dumps = dumper

    def set_data(self, data):
        """

        set data to client

        :param data: any response data
        :return: self
        """
        self.status = "OK"
        self.data = data
        return self

    def set_error(self, msg: str):
        """
        in case of error set error message

        :param msg: error text
        :return: self
        """
        self.status = "ERROR"
        self.message = msg
        return self

    def __call__(self, *args, **kwargs):
        json_object = {'type': self.type,
                       'status': self.status}
        if self.status == "OK":
            json_object['data'] = self.data
        else:
            json_object['message'] = self.message

        return self._dumps(json_object)
