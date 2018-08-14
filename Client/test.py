import traceback


def try_except(function):
    def wrapper(*args, **kwargs):
        try:
            return function(*args, **kwargs)
        except:
            print(args, kwargs)
            traceback.print_exc()
    return wrapper