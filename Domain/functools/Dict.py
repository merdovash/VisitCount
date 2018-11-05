from Domain.Primitives import value_of


def without(d, *keys) -> dict:
    new_dict = {}

    for key in d:
        if key not in keys:
            new_dict[key] = d[key]

    return new_dict


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
