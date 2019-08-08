"""
This module contains static class methods to read and load json.

TODO:
    * decoding
    * encoding
"""
import json
from datetime import datetime, date
from enum import Enum

from sqlalchemy.ext.associationproxy import _AssociationList

from Domain.Exception.Net import InvalidPOSTDataException
from Domain.Structures.DictWrapper import Structure
from Parser import IJSON

DATE_FORMAT = "%Y-%m-%d %H:%M:%S"


class JsonParser:
    """
    custom class to read and dumps json
    """

    @staticmethod
    def read(text: str):
        """

        :param text: json encoded string
        :return: json object
        """

        def decode(val) -> str:
            """

            :param val: encoded string
            :return: decoded string
            """
            return val

        res = None

        if text is not None and text != "":
            res = json.loads(decode(text))
        else:
            raise InvalidPOSTDataException(text)

        return res

    @staticmethod
    def dump(obj):
        """

        :param obj: object
        :return: encoded json string
        """

        def encode(val) -> str:
            """

            :param val: string
            :return: encoded string
            """
            return val

        if obj is None or obj == 'None':
            res = "null"
        elif isinstance(obj, dict):
            res = "{"
            for key in obj.keys():
                value = obj[key]
                if isinstance(value, (int, str, bool, float)) or value is None:
                    res += f'"{key}":"{value}",'
                else:
                    res += f'"{key}":{JsonParser.dump(obj[key])},'
            else:
                res = res[:-1] if len(res) > 1 else res
            res += "}"

        elif isinstance(obj, (list, _AssociationList)):
            res = "["

            for item in obj:
                res += f'{JsonParser.dump(item)},'
            else:
                res = res[:-1] if len(res) > 1 else res
            res += "]"

        elif isinstance(obj, Structure.__class__):
            res = f'"{obj.class_name()}"'

        elif isinstance(obj, IJSON) or hasattr(obj, 'to_json'):
            res = obj.to_json()

        elif isinstance(obj, (int, str, bool, float)) or obj is None:
            res = f'"{obj}"'

        elif isinstance(obj, (datetime, date)):
            res = f'"{obj.strftime("%Y-%m-%d %H:%M:%S")}"'

        elif isinstance(obj, Enum):
            res = f'"{str(obj).split(".")[1]}"'

        else:
            res = json.dumps(encode(obj)).encode("utf-8")

        return res
