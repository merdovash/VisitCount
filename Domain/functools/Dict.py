from typing import Dict

from DataBase2 import Base
from Domain.Primitives import value_of


def format_view(d: Dict[str, str]):
    for key in ['last_name', 'first_name', 'middle_name']:
        d[key] = d[key].capitalize()
    return d


def validate_new_user(d: Dict):
    for key in ['last_name', 'first_name', 'middle_name', 'email']:
        if key not in d.keys() or d[key] == "" or d[key] is None:
            return False
    else:
        return True


def to_dict(obj):
    if isinstance(obj, Base):
        res = {}

        columns = list(map(lambda x: x.name, obj.__table__._columns))

        for column_name in columns:
            res[column_name] = obj.__getattribute__(column_name)

        return res
    else:
        raise NotImplementedError(f'item {obj} is instance of {type(obj)}')


def without(d, *keys) -> dict:
    new_dict = {}

    for key in d:
        if key not in keys:
            new_dict[key] = d[key]

    return new_dict


def fix_values(d: dict) -> dict:
    new_d = {}
    for key, value in d.items():
        new_d[key] = value_of(value)
    return new_d


def fix_keys(d) -> dict:
    _d = {}

    for key in d.keys():
        real_key = value_of(key)
        if real_key not in _d.keys():
            _d[real_key] = d[key]
        elif isinstance(d[key], list):
            if isinstance(_d[real_key], list):
                _d[real_key].append()
            else:
                raise TypeError(f'cannot merge {d[key]} and {_d[real_key]}')
        elif isinstance(d[key], dict):
            if isinstance(_d[real_key], dict):
                _d[real_key].update(d[key])
            else:
                raise TypeError(f'cannot merge {d[key]} and {_d[real_key]}')
        else:
            raise NotImplementedError(type(d[key]))

    return _d
