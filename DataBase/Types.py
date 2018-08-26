"""
This module contains all Structures, Classes and Functions needed in DataBase.
"""
from collections import namedtuple
from typing import Dict


def format_name(user: Dict[str, str]):
    """
    Do format user data to readable string
    :param user: dictionary that contains keys: [last_name, first_name, middle_name]
    :return: string like 'Mark A.F.'
    """

    middle_name_len = len(user['middle_name'])
    if middle_name_len > 0:
        result = f'{user["last_name"]} {user["first_name"][0]}.{user["middle_name"][0]}.'
    else:
        result = f'{user["last_name"]} {user["first_name"][0]}.'

    return result


Table = namedtuple('Table', 'name columns extra')
Column = namedtuple('Column', 'name type spec')


class AtrDict(dict):
    """
    This class is dictionary wrapper to looks like a object
    """

    def __init__(self, d: dict, **kwargs):
        super().__init__(d, **kwargs)

        for key in d.keys():
            if isinstance(d[key], dict):
                self[key] = AtrDict(d[key])

    def __getattr__(self, name) -> Column:
        if name in self:
            return self[name]
        else:
            raise AttributeError("No such attribute: " + name)

    def __setattr__(self, name, value):
        self[name] = value

    def __delattr__(self, name):
        if name in self:
            del self[name]
        else:
            raise AttributeError("No such attribute: " + name)


def cached(func):
    cache = {}

    def __wrapper__(*args, **kwargs):
        args_hash = hash((args, tuple(sorted(kwargs.items()))))
        print('cache: ', args_hash in cache.keys())
        if args_hash not in cache.keys():
            res = func(*args, **kwargs)
            cache[args_hash] = res
        return cache[args_hash]

    return __wrapper__
