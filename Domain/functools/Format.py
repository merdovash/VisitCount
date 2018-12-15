from typing import Dict, List

import pymorphy2

from DataBase2 import Professor, Student, Administration, Parent
from Domain.Exception.Constraint import ConstraintBasenameException, ConstraintDictNameException


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
    elif isinstance(user, (Student, Professor, Administration, Parent)):
        if len(user.middle_name) > 0:
            fio = [user.last_name, user.first_name, user.middle_name]
        else:
            fio = [user.last_name, user.first_name]
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
