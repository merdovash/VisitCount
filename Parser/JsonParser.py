"""
This module contains static class methods to read and load json.

TODO:
    * decoding
    * encoding
"""
import json
from datetime import datetime, date

from DataBase2 import Base
from Exception import InvalidPOSTDataException

date_format = "%Y-%m-%d %H:%M:%f"


def to_json(obj):
    if isinstance(obj, Base):
        res = {}

        columns = list(map(lambda x: x.name, obj.__table__._columns))

        for column_name in columns:
            res[column_name] = obj.__getattribute__(column_name)

        return JsonParser.dump(res)
    else:
        raise NotImplementedError()


def to_db_object(type_name: str, net_dict: dict):
    """

    :param type_name: название типа в orm
    :param net_dict:
    :return:
    """
    if 'date' in net_dict:
        net_dict['date'] = datetime.strptime(net_dict['date'],
                                             "%Y-%m-%dT%H:%M:%S")

    class_ = eval(f'DataBase2.{type_name}')

    res = class_(**net_dict)

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
                res = res[:-1]
            res += "}"

        elif isinstance(obj, list):
            res = "["

            for item in obj:
                res += f'{JsonParser.dump(item)},'
            else:
                res = res[:-1]
            res += "]"

        elif isinstance(obj, Base):
            res = to_json(obj)

        elif isinstance(obj, (int, str, bool, float)) or obj is None:
            res = f'"{obj}"'

        elif isinstance(obj, (datetime, date)):
            res = f'"{obj.isoformat()}"'

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
