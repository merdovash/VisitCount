from datetime import datetime


def int_of(val):
    if isinstance(val, int):
        return val
    elif isinstance(val, str):
        if val.isnumeric():
            return int(val)
        else:
            raise TypeError(f'{val} is not int')
    else:
        raise NotImplementedError(type(val))


def value_of(val) -> str or int or bool:
    if isinstance(val, int):
        return val
    elif isinstance(val, str):
        if val.isnumeric():
            return int(val)
        elif val in ['True', 'False']:
            return eval(val)
        else:
            return val
    elif isinstance(val, datetime):
        return val
    else:
        raise NotImplementedError(type(val))
