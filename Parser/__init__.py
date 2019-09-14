# encoding: utf8
import enum
import os

from sqlalchemy.engine import url

from Domain.Exception import BisitorException

_args = None


class Side(enum.Enum):
    client = 0
    server = 1


class IJSON:
    def to_json(self):
        raise NotImplementedError()


def Args(side='client'):
    global _args
    if _args is None:
        if side == 'client':
            from Parser.ClientConfiguration import Config
            _args = Config()
            _args.side = Side.client

        elif side == 'server':
            from Parser.ServerConfiguration import Config
            _args = Config()
            _args.side = Side.server
        else:
            raise BisitorException("Необходимо обьявить тип приложения")
    return _args

