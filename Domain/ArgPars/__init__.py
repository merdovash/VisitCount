import sys


def get_argv(arg_name, next=False, default=None):
    try:
        index = sys.argv.index(arg_name)
        if next:
            return sys.argv[index+1]
        else:
            return sys.argv[index]
    except ValueError:
        return default
