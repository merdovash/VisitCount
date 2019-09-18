from typing import Type

from DataBase2 import DBObject


class Validate:
    @staticmethod
    def without_None(d) -> dict:
        return {key: item for key, item in d.items() if item is not None}


class Map:
    @staticmethod
    def item_type(d: dict, class_: Type[DBObject]) -> dict:
        return {key: class_.column_type(key)(value) for key, value in d.items()}
