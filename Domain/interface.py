from typing import TypeVar, Type

from Domain.Exception import BisitorException

CLS = TypeVar('CLS')


class SingletonError(BisitorException):
    pass


class Singleton:
    @classmethod
    def instance(cls: Type[CLS], **kwargs)->CLS:
        if not hasattr(cls, '_inst') or cls._inst is None:
            cls._inst = cls(**kwargs)
        return cls._inst

    def __init__(self):
        if hasattr(self, '_inst') and self._inst is not None:
            raise SingletonError()
