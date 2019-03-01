import functools
import sys
import traceback
from itertools import chain

from Domain.functools.List import DBList


def is_iterable(item):
    try:
        iterator = iter(item)
    except TypeError:
        return False
    else:
        return True


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


def listed(func):
    def __wrapper__(self, value, *args, **kwargs):
        if is_iterable(value):
            result = [func(self, v, *args, **kwargs) for v in value]
            if any(is_iterable(sub_res) for sub_res in result):
                res = list(set(chain.from_iterable(result)))
            else:
                res = list(set(result))
        else:
            res = func(self, value, *args, **kwargs)

        if len(res) and is_iterable(res[0]):
            return list(set(chain.from_iterable(res)))
        else:
            return list(set(res))

    return __wrapper__


def filter_deleted(func):
    def __wrapper__(self, value, with_deleted=False, *args, **kwargs):
        return list(filter(lambda x: (not x._is_deleted) | with_deleted, func(self, value, *args, **kwargs)))
    return __wrapper__


def sorter(func):
    def __wrapper__(self, value, sort=None, *args, **kwargs):
        res = func(self, value, *args, **kwargs)
        if sort is None:
            return res
        return sorted(res, key=sort)
    return __wrapper__


if __name__ == '__main__':
    from DataBase2 import Parent, Professor, Student, Lesson, Group, Discipline

    print(Group.of(Professor.get(id=1)))
    print(Group.of(Discipline.of(Professor.get(id=1))))