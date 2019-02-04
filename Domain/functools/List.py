import datetime
from typing import List, TypeVar

from sqlalchemy.ext.associationproxy import _AssociationList

T = TypeVar('T')


class DBList(list):
    is_flat = False
    is_unique = False
    with_deleted = True

    def __init__(self, l=None, flat=False, unique=False, with_deleted=True):
        if l is None:
            super().__init__()
        else:
            super().__init__(l)

        if flat:
            self.to_flat()
        if unique:
            self.to_unique()
        if not with_deleted:
            self.remove_deleted()

    @staticmethod
    def wrapper(func):
        def __DBList_func_wrapper__(*args, **kwargs):
            with_deleted = kwargs.get('with_deleted', False)
            flat = kwargs.get('flat', False)
            unique = kwargs.get('unique', False)

            res = func(*args, **kwargs)

            return DBList(res, with_deleted=with_deleted, flat=flat, unique=unique)
        return __DBList_func_wrapper__

    def unique(self) -> 'DBList':
        new_list = DBList()
        for item in self:
            if isinstance(item, (list, _AssociationList)):
                item = frozenset(item)
            if item not in new_list:
                new_list.append(item)

        for i, item in enumerate(new_list):
            if isinstance(item, frozenset):
                new_list[i] = list(item)

        new_list.is_unique = True
        return new_list

    def is_empty(self) -> bool:
        return len(self) == 0

    def without_deleted(self: List[T] or T) -> 'DBList':
        return DBList(filter(lambda x: not x._is_deleted, self))

    def remove_deleted(self) -> 'DBList':
        i = 0
        while i < len(self):
            if isinstance(self[i], DBList):
                self[i].remove_deleted()
                if len(self[i]) == 0:
                    self.pop(i)
                    i -= 1
            elif isinstance(self[i], frozenset):
                temp = DBList(self[i], with_deleted=False)
                self[i] = frozenset(temp)
            else:
                if self[i] is None or self[i]._is_deleted:
                    self.pop(i)
                    i -= 1
            i += 1

        self.with_deleted = False
        return self

    def __and__(self, other) -> 'DBList':
        return DBList(set(self) & set(other))

    def find(self, func, default=None):
        res = list(filter(func, self))
        if len(res) > 0:
            return res[0]
        else:
            return default

    def without_None(self) -> 'DBList':
        new = DBList()
        for item in self:
            if item is not None:
                new.append(item)
        return new

    def remove_None(self) -> 'DBList':
        i = 0
        while i < len(self):
            if self[i] is None:
                self.pop(i)
                i -= 1
            i += 1
        return self

    def flat(self) -> 'DBList':
        new_list = DBList()
        for item in self:
            if isinstance(item, (list, _AssociationList)):
                new_list.extend(DBList(item).flat())
            else:
                new_list.append(item)

        new_list.is_flat = True
        return new_list

    def to_flat(self):
        i = 0
        while i < len(self):
            if isinstance(self[i], list):
                item = DBList(self[i], flat=True)
                self.pop(i)
                for index in range(len(item)):
                    self.insert(i, item[index])
                    i += 1
                i -= 1
            i += 1

        self.is_flat = True
        return self

    def to_unique(self):
        packed = False
        if any([isinstance(o, list) for o in self]):
            for index, item in enumerate(self):
                if isinstance(item, list):
                    self[index] = frozenset(item)
            packed = True

        temp = set(self)
        self.clear()
        self.extend(temp)
        self.is_unique = True

        if packed:
            for index, item in enumerate(self):
                if isinstance(item, frozenset):
                    self[index] = DBList(item)

        return self


def without_None(l) -> List:
    new = DBList()
    for item in l:
        if item is not None:
            new.append(item)
    return new


def find(func, l, default=None):
    res = list(filter(func, l))
    if len(res) > 0:
        return res[0]
    else:
        return default


def closest_lesson(lessons: list, date_format="%d-%m-%Y %I:%M%p"):
    """

    :param date_format:
    :param lessons: list of lessons
    :return: closest lesson in list to current datetime
    """
    if len(lessons) == 0:
        return None
    closest = min(
        lessons,
        key=lambda x: abs(datetime.datetime.now() - x.date))
    return closest