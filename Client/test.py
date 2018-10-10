import sys
import traceback


def safe(func):
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except:
            exc_info = sys.exc_info()
            stack = traceback.extract_stack()
            tb = traceback.extract_tb(exc_info[2])
            full_tb = stack[:-1] + tb
            exc_line = traceback.format_exception_only(*exc_info[:2])
            # print("Traceback (most recent call last):")
            # print("".join(traceback.format_list(full_tb)))
            # print("".join(exc_line))
    return wrapper