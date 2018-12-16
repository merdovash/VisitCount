"""
This module contains static class methods to read and load json.

TODO:
    * decoding
    * encoding
"""
import json
from datetime import datetime, date

from sqlalchemy.ext.associationproxy import _AssociationList

from DataBase2 import Base
from Domain.Exception.Net import InvalidPOSTDataException
from Domain.functools.Dict import without, to_dict

date_format = "%Y-%m-%d %H:%M:%f"


def to_json(obj):
    return JsonParser.dump(to_dict(obj))


def to_db_object(type_name: str, net_dict: dict):
    """

    :param type_name: название типа в orm
    :param net_dict:
    :return:
    """
    if 'date' in net_dict:
        net_dict['date'] = datetime.strptime(net_dict['date'],
                                             "%Y-%m-%dT%H:%M:%S")

    if 'active' in net_dict:
        net_dict['active'] = eval(net_dict['active'])

    if isinstance(type_name, str):
        exec(f'from DataBase2 import {type_name}')
        class_ = eval(type_name)
    elif isinstance(type_name, type):
        class_ = type_name
    else:
        raise NotImplementedError(type(type_name))

    res = class_(**without(net_dict, 'new_index'))

    return res


class IJSON:
    def to_json(self):
        raise NotImplementedError()


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

        res = ""

        if isinstance(obj, dict):
            res = "{"
            for key in obj.keys():
                value = obj[key]
                if any(map(lambda x: isinstance(value, x),
                           [int, str, bool, float])) or value is None:
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

        elif isinstance(obj, Base):
            res = to_json(obj)

        elif isinstance(obj, (int, str, bool, float)) or obj is None:
            res = f'"{obj}"'

        elif isinstance(obj, (datetime, date)):
            res = f'"{obj.isoformat()}"'

        elif hasattr(obj, 'to_json'):
            res = obj.to_json()
        else:
            res = json.dumps(encode(obj)).encode("utf-8")

        return res


def test():
    obj = to_db_object("Student",
                       {"last_name": "sfsdg", "first_name": "fddhgfh",
                        "middle_name": "dsdhdhdh"})
    print(to_json(obj))

    dumped = JsonParser.dump({
        'Student': [obj, {'fgr': [1, 2, 3, None, "13343", 1.45],
                          'fghn': "rftvybuhnj"}]
    })
    print(dumped)

    print(JsonParser.read(dumped))
