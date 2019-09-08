# encoding=utf8

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
            print(decode(text))
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
                if isinstance(value, (int, str, float)):
                    if isinstance(obj, str):
                        res += '"'+key+'":"' + value.replace("\"", "\\\"").replace('None', 'null')+'",'
                    else:
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

        elif isinstance(obj, type):
            if hasattr(obj, 'class_name'):
                res = f'"{obj.class_name()}"'
            else:
                res = f'"{obj.__name__}"'

        elif isinstance(obj, IJSON) or hasattr(obj, 'to_json'):
            res = obj.to_json()

        elif isinstance(obj, (int, str, float)) or obj is None:
            res = "\"" + obj.replace("\"", "\\\"") if isinstance(obj, str) else str(obj) + "\""

        elif isinstance(obj, bool):
            res = 'true' if obj else 'false'

        elif isinstance(obj, (datetime, date)):
            res = f'"{obj.strftime("%Y-%m-%d %H:%M:%S")}"'

        elif isinstance(obj, Enum):
            res = f'"{str(obj).split(".")[1]}"'

        else:
            res = json.dumps(encode(obj), ensure_ascii=False).encode("utf-8")

        return res


if __name__ == '__main__':
    print(JsonParser.read('{"request_type":"api/user/first_load","status":"OK","data":{"auth":{"id":"1","login":"Vlad","password":"123456","uid":"None","user_type":"PROFESSOR","user_id":"1"},"professor":[{"id":"1","_created":"2019-09-08 11:39:02","_updated":"2019-09-08 11:39:02","_is_deleted":"False","_deleted":"None","last_name":"Щекочихин","first_name":"Владсилав","middle_name":"","card_id":"None","_last_update_in":"2019-09-08 11:39:02","settings":"{\"colors\": {\"_type\": \"Area\", \"title\": \"Цвета Журнала посещений\", \"visit\": {\"_type\": \"color\", \"title\": \"Цвет посещения\", \"value\": \"rgb(138, 226, 52)\", \"default\": \"rgb(240, 240, 0)\"}, \"sub_visit\": {\"_type\": \"color\", \"title\": \"Цвет уважительного пропуска\", \"value\": None, \"default\": \"rgb(255, 238, 238)\"}, \"not_visited\": {\"_type\": \"color\", \"title\": \"Цвет пропуска\", \"value\": \"rgb(226, 61, 135)\", \"default\": \"rgb(255, 255, 255)\"}, \"not_completed\": {\"_type\": \"color\", \"title\": \"Цвет непроведенного занятия\", \"value\": None, \"default\": \"rgb(199, 199, 199)\"}, \"good_student\": {\"_type\": \"color\", \"title\": \"Цвет обозначения хорошего уровня посещений\", \"value\": \"rgb(115, 210, 22)\", \"default\": \"rgb(0, 255, 0)\"}, \"bad_student\": {\"_type\": \"color\", \"title\": \"Цвет обозначения плохого уровня посещений\", \"value\": \"rgb(239, 41, 41)\", \"default\": \"rgb(255, 0, 0)\"}, \"avg_student\": {\"_type\": \"color\", \"title\": \"Цвет обозначения среднего уровня посещений\", \"value\": None, \"default\": \"rgb(255, 255, 255)\"}, \"missing_card\": {\"_type\": \"color\", \"title\": \"Цвет студентов без зарегистрованной карты\", \"value\": None, \"default\": \"rgb(121, 22, 22)\"}}}","contact_info_id":"1"}],"data":{"Lesson":[],"Visitation":[],"StudentsParents":[],"Faculty":[],"VisitationLossReason":[],"LessonType":[],"Discipline":[],"Student":[],"Building":[],"DataView":[],"StudentsGroups":[],"File":[],"Administration":[],"Department":[],"Group":[],"LessonsGroups":[],"ContactViews":[],"Parent":[],"Semester":[],"Room":[],"ContactInfo":[{"id":"1","_created":"2019-09-08 11:39:02","_updated":"2019-09-08 11:39:02","_is_deleted":"False","_deleted":"None","email":"","auto":"False","last_auto":"2010-01-01 00:00:00"}],"DepartmentProfessors":[]}},"message":null,"data_type":"Domain.Structures.DictWrapper.Network.FirstLoad.ServerFirstLoadData"}'))
