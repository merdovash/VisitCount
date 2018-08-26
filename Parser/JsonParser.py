"""
This module contains static class methods to read and load json.

TODO:
    * decoding
    * encoding
"""
import json


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

        return json.dumps(encode(obj)).encode("utf-8")
