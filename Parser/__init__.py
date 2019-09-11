# encoding: utf8
import enum
import os

from sqlalchemy.engine import url

from Domain.Exception import BisitorException
from Parser.ServerConfiguration import Config

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
        import argparse
        if side == 'client':
            from Client.src import src
            parser = argparse.ArgumentParser(description="Process parameters")
            parser.add_argument('--host', metavar='H', default='http://bisitor.itut.ru', type=str,
                                help='you can specify server host address', dest='host')
            parser.add_argument('--test', type=bool, default=False, help='for testing without Reader')
            parser.add_argument('--css', type=str, default=src.qss, help='you can disable css')

            _args, _ = parser.parse_known_args()
            _args.side = Side.client

        elif side == 'server':
            _args = Config()
            _args.side = Side.server
        else:
            raise BisitorException("Необходимо обьявить тип приложения")
    return _args

