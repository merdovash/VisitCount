"""
This module contains all Structures, Classes and Functions needed in DataBase.
"""
from collections import namedtuple
from typing import Dict, List

import pymorphy2

from DataBase2 import Professor, Student, Administration, Parent


class ConstraintDictNameException(KeyError):
    def __init__(self):
        super().__init__('Dict must contain keys: "last_name", "first_name", [Optional: "middle_name"]')


class ConstraintBasenameException(KeyError):
    def __init__(self):
        super().__init__('Base must contains fields: last_name, first_name, [Optional: middle_name]')


def format_name(user: Dict[str, str] or Professor or Student, case=None):
    """
    Do format user data to readable string
    :param user: dictionary that contains keys: [last_name, first_name, middle_name]
    :return: string like 'Mark A.F.'
    """
    fio: List = []
    if isinstance(user, dict):
        try:
            if 'middle_name' in user.keys():
                middle_name_len = len(user['middle_name'])
                if middle_name_len > 0:
                    fio = [user["last_name"], user["first_name"], user["middle_name"]]
                else:
                    fio = [user["last_name"], user["first_name"]]
            else:
                fio = [user["last_name"], user["first_name"]]
        except KeyError:
            raise ConstraintDictNameException()
    elif isinstance(user, (Student, Professor, Administration, Parent)):
        if len(user.middle_name) > 0:
            fio = [user.last_name, user.first_name, user.middle_name]
        else:
            fio = [user.last_name, user.first_name]
    else:
        try:
            if hasattr(user, 'middle_name') and len(user.middle_name) > 0:
                fio = [user.last_name, user.first_name, user.middle_name]
            else:
                fio = [user.last_name, user.first_name]
        except KeyError:
            raise ConstraintBasenameException()

    if case is not None:
        morph = pymorphy2.MorphAnalyzer()
        fio = [morph.parse(name)[0].inflect(case).word for name in fio]

    return ' '.join([f.capitalize() for f in fio])


Table = namedtuple('Table', 'name columns extra')
column = namedtuple('Column', 'name type primary_key unique')


def Column(name, field_type, primary_key=False, unique=False) -> column:
    if primary_key == '':
        primary_key = False
    return column(name=name, type=field_type, primary_key=primary_key, unique=unique)


class AtrDict(dict):
    """
    This class is dictionary wrapper to looks like a object
    """

    def __init__(self, d: dict, **kwargs):
        super().__init__(d, **kwargs)

        for key in d.keys():
            if isinstance(d[key], dict):
                self[key] = AtrDict(d[key])

    def __getattr__(self, name) -> column:
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
        args_hash = hash((args[1:], tuple(sorted(kwargs.items()))))
        print('cache: ', (args[1:], tuple(sorted(kwargs.items()))), args_hash in cache.keys())
        if args_hash not in cache.keys():
            res = func(*args, **kwargs)
            cache[args_hash] = res
        return cache[args_hash]

    return __wrapper__
