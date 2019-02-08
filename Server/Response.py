"""
response builder module
"""
from enum import Enum
from typing import Type, Dict, Any

from Domain.Structures.DictWrapper import Structure


class Response(Structure):
    """
    main class of response builder
    """

    class Status(Enum):
        OK = 1
        ERROR = 0

        @classmethod
        def get(cls, msg):
            if msg == "OK":
                return cls.OK
            if msg == "ERROR":
                return cls.ERROR

    request_type: str
    data_type: str or Type[Structure]
    status: 'Response.Status'
    data: Dict or Structure
    message: str = None

    def __init__(self, request_type):
        self.request_type = request_type
        self.status = None
        self.data = None
        self.message = None

    def set_data(self, data: Any, data_type: Type[Structure] = None):
        """

        set data to client

        :param data_type: type of Wrapper
        :param data: any response data
        :return: self
        """
        self.status = self.Status.OK
        self.data = data
        if data_type is not None:
            self.data_type = data_type
        else:
            self.data_type = str(type(data)).split("'")[1]
        return self

    def set_error(self, msg: str):
        """
        in case of error set error message

        :param msg: error text
        :return: self
        """
        self.status = self.Status.ERROR
        self.message = msg
        return self

    def __call__(self):
        return self.to_json()

    @classmethod
    def load(cls, class_: Type[Structure] = None, **kwargs) -> 'Response':
        self = cls(kwargs.get('request'))
        self.request_type = kwargs.get('request_type')

        self.status = cls.Status[kwargs.get('status')]

        if self.status == self.Status.OK:
            if class_ is not None:
                self.data = Structure.load(kwargs.get('data', {}), class_=class_)

            elif kwargs.get('data_type', None) is not None:
                self.data_type: str = kwargs.get('data_type', None)
                self.data = Structure.load(kwargs.get('data', {}), self.data_type)

            else:
                self.data = kwargs.get('data')

        else:
            self.message = kwargs.get('message')

        return self
