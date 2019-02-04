import sys


def get_argv(arg_name, is_next=False, default=None):
    try:
        index = sys.argv.index(arg_name)
        if is_next:
            return sys.argv[index+1]
        return sys.argv[index]
    except ValueError:
        return default
