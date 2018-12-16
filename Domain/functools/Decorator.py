import functools
import sys
import traceback


def memoize(obj):
    """
    Кэширует все уникальные вызовы функции
    !!! осторожно с методами классов

    :param obj: декорируемая функция
    :return: декоратор
    """
    cache = obj.cache = {}

    @functools.wraps(obj)
    def memoizer(*args, **kwargs):
        key = str(args) + str(kwargs)
        if key not in cache:
            cache[key] = obj(*args, **kwargs)
        return cache[key]

    return memoizer


def safe(func):
    """
    Оборачивает функцию в try/catch блок и выводит полный traceback
    Используется для PyQt, который завершает приложение без сообщения ошибки.

    :param func: функция, которая оборачивается
    :return: декорирующая функция
    """

    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except:
            exc_info = sys.exc_info()
            stack = traceback.extract_stack()
            tb = traceback.extract_tb(exc_info[2])
            full_tb = stack[:-1] + tb
            exc_line = traceback.format_exception_only(*exc_info[:2])
            print("Traceback (most recent call last):")
            print("".join(traceback.format_list(full_tb)))
            print("".join(exc_line))
            raise

    return wrapper
