class Validate:
    @staticmethod
    def card_id(val):
        return val is not None and val != '' and val != 'None'


class Get:
    @staticmethod
    def table_name(val) -> str:
        from DataBase2 import Base
        if isinstance(val, str):
            return val
        elif isinstance(val, type):
            return val.__name__
        elif isinstance(val, Base):
            return type(val).__name__
        else:
            raise NotImplementedError()
