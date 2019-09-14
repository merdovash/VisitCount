from datetime import datetime

from Domain.Exception.Constraint import CardIdValueException


class Validate:
    @staticmethod
    def card_id(val):
        if isinstance(val, int):
            return True
        elif isinstance(val, str):
            if val.isnumeric():
                return True
        return False


class Get:

    @staticmethod
    def table_name(val) -> str:
        from sqlalchemy.ext.declarative import DeclarativeMeta
        from DataBase2 import _DBObject, Base
        if isinstance(val, str) and val in [cls.__name__ for cls in _DBObject.subclasses()]:
            return val
        elif isinstance(val, DeclarativeMeta):
            return val.__name__
        elif isinstance(val, Base):
            return type(val).__name__
        else:
            raise NotImplementedError()

    @staticmethod
    def bool(val) -> bool or None:
        if not val:
            return False
        if val in ['True', 'true', '1', 1, True]:
            return True
        if val in [False, 'False', 'false', '0', 0, None, 'None', 'null', '']:
            return False
        raise ValueError(f'invalid value for bool: "{val}" type of {type(val)}')

    @staticmethod
    def datetime(val) -> datetime or None:
        if val is None or val == 'None' or val == 'null':
            return None
        else:
            if isinstance(val, str):
                return datetime.strptime(val, "%Y-%m-%d %H:%M:%S")
            if isinstance(val, datetime):
                return val
            raise NotImplementedError(type(val))

    @staticmethod
    def int(val) -> int or None:
        if val in [None, 'None', 'null']:
            return None
        if isinstance(val, int):
            return val
        if isinstance(val, str):
            try:
                return int(val)
            except ValueError:
                return None
        if val is None:
            return None
        raise NotImplementedError(type(val))

    @staticmethod
    def card_id(val) -> int or None:
        if isinstance(val, str):
            try:
                return int(val)
            except ValueError:
                if val in ['None', 'none', 'null', '']:
                    return None
                raise CardIdValueException()
        if isinstance(val, (int, float)):
            return int(val)
        if val is None:
            return None
        raise NotImplementedError()
