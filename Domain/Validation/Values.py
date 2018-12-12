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
        from DataBase2 import Base
        from sqlalchemy.ext.declarative import DeclarativeMeta
        if isinstance(val, str) and val in [cls.__name__ for cls in Base.__subclasses__()]:
            return val
        elif isinstance(val, DeclarativeMeta):
            return val.__name__
        elif isinstance(val, Base):
            return type(val).__name__
        else:
            raise NotImplementedError()
