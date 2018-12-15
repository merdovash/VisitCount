from typing import Dict, List

import pymorphy2

from DataBase2 import Professor, Student, Administration, Parent
from Domain.Exception.Constraint import ConstraintBasenameException, ConstraintDictNameException, \
    ConstraintNotEmptyException
from Domain.functools.Function import None_or_empty


class Case(object):
    nomn = {'nomn'}
    gent = {'gent'}
    datv = {'datv'}
    accs = {'accs'}
    ablt = {'ablt'}
    loct = {'loct'}


def format_name(user: Dict[str, str] or Professor or Student, case=None) -> str:
    """
    Do format user data to readable string
    :param user: dictionary that contains keys: [last_name, first_name, middle_name]
    :return: string like 'Mark A.F.'
    """
    fio: List = []
    if isinstance(user, dict):
        try:
            if 'middle_name' in user.keys():
                middle_name_len = len(user['middle_name'])
                if middle_name_len > 0:
                    fio = [user["last_name"], user["first_name"], user["middle_name"]]
                else:
                    fio = [user["last_name"], user["first_name"]]
            else:
                fio = [user["last_name"], user["first_name"]]
        except KeyError:
            raise ConstraintDictNameException()
        else:
            for key, val in user.items():
                if val in fio and None_or_empty(user[key]):
                    raise ConstraintNotEmptyException(key)
    elif isinstance(user, (Student, Professor, Administration, Parent)):
        if not None_or_empty(user.last_name) and not None_or_empty(user.first_name):
            if not None_or_empty(user.middle_name):
                fio = [user.last_name, user.first_name, user.middle_name]
            else:
                fio = [user.last_name, user.first_name]
        else:
            if None_or_empty(user.last_name):
                raise ConstraintNotEmptyException('last_name')
            else:
                raise ConstraintNotEmptyException('first_name')
    else:
        try:
            if hasattr(user, 'middle_name') and len(user.middle_name) > 0:
                fio = [user.last_name, user.first_name, user.middle_name]
            else:
                fio = [user.last_name, user.first_name]
        except KeyError:
            raise ConstraintBasenameException()

    if case is not None:
        morph = pymorphy2.MorphAnalyzer()
        fio = [morph.parse(name)[0].inflect(case).word for name in fio]

    return ' '.join([f.capitalize() for f in fio])
