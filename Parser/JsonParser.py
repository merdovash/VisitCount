import json


class jsonParser:
    @staticmethod
    def read(val: str):
        """

        :param val: json encoded string
        :return: json object
        """

        def decode(v) -> str:
            # TODO: сделать
            """

            :param v: encoded string
            :return: decoded string
            """
            return v

        if val is not None and val != "":
            return json.loads(decode(val))
        else:
            return None

    @staticmethod
    def dump(val):
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
