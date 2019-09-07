from typing import Dict, List, Any

import pymorphy2

from DataBase2 import _DBNamed, _DBObject
from Domain.functools.Decorator import is_iterable


def js_format(js: str, **kwargs):
    for key, val in kwargs.items():
        js = js.replace('{' + key + '}', str(val))

    return js


def names(args: List[_DBNamed]):
    if any(len(s.full_name()) > 25 for s in args):
        return ', '.join(s.short_name() for s in args)
    return ', '.join(s.full_name() for s in args)


def type_name(value: Any) -> str:
    if isinstance(value, type):
        if issubclass(value, _DBObject):
            return value.__type_name__
        else:
            return value.__name__
    if isinstance(value, _DBObject):
        return value.__type_name__
    if is_iterable(value):
        if len(value) > 0:
            if all(type(v) == type(value[0]) for v in value):
                if isinstance(value[0], _DBObject):
                    return value[0].__type_name__
                else:
                    return type(value[0]).__name__
            else:
                return ', '.join(type_name(v) for v in value)
        else:
            return '[]'

