def without_None(items):
    return [i for i in items if i]


def find(func, l, default=None):
    res = list(filter(func, l))
    if len(res) > 0:
        return res[0]
    else:
        return default