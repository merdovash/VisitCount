from typing import TypeVar, Type, List


DB = TypeVar('DB')


class ISession:
    def commit(self):
        pass

    def query(self, table: Type[DB]):
        class IJoinable:
            def join(self, table: Type) -> 'IJoinable':
                pass

            def all(self)->List[DB]:
                pass

            def first(self) -> DB:
                pass

        return IJoinable()

    def flush(self):
        pass

    def expire_all(self):
        pass

    def add(self, obj: '_DBObject'):
        pass

    def close(self):
        pass