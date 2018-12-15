import functools


def memoize(obj):
    cache = obj.cache = {}

    @functools.wraps(obj)
    def memoizer(*args, **kwargs):
        key = str(args) + str(kwargs)
        if key not in cache:
            cache[key] = obj(*args, **kwargs)
        return cache[key]

    return memoizer


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
