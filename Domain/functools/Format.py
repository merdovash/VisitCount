from typing import Dict, List, Any
from warnings import warn

import pymorphy2

from DataBase2 import Professor, Student, _DBPerson, _DBNamed, _DBObject
from Domain.Exception.Constraint import ConstraintBasenameException, ConstraintDictNameException, \
    ConstraintNotEmptyException
from Domain.functools.Decorator import is_iterable
from Domain.functools.Function import None_or_empty


class Case(object):
    nomn = {'nomn'}
    gent = {'gent'}
    datv = {'datv'}
    accs = {'accs'}
    ablt = {'ablt'}
    loct = {'loct'}


def format_name(user: Dict[str, str] or Professor or Student, case: set = None, small=False) -> str:
    """
    Do format user data to readable string
    :param small: в краткой форме
    :param case: падеж
    :param user: dictionary that contains keys: [last_name, first_name, middle_name]
    :return: string like 'Mark A.F.'
    """
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
    elif isinstance(user, _DBPerson):
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
        first_name = list(filter(
            lambda x: x.tag.case == 'nomn',
            morph.parse(fio[1])))[0]

        last_name = list(filter(
            lambda x: x.tag.case == 'nomn' and first_name.tag.gender == first_name.tag.gender,
            morph.parse(fio[0])))[0]

        if len(fio) == 3:
            middle_name = list(filter(
                lambda x: x.tag.case == 'nomn' and first_name.tag.gender == first_name.tag.gender,
                morph.parse(fio[2])))[0]

            fio = [x.inflect(case).word for x in [last_name, first_name, middle_name]]

        else:
            fio = [x.inflect(case).word for x in [last_name, first_name]]

    if small:
        return ' '.join([f.capitalize() if i == 0 else f.capitalize()[0] + '.' for i, f in enumerate(fio)])
    return ' '.join([f.capitalize() for f in fio])


def js_format(js: str, **kwargs):
    for key, val in kwargs.items():
        js = js.replace('{' + key + '}', str(val))

    return js


def agree_to_number(word: str, number: int) -> str:
    morph = pymorphy2.MorphAnalyzer()
    word = morph.parse(word)[0]
    if number not in [-1, 1]:
        word = word.make_agree_with_number(number)
    return word.word


def inflect(text, case) -> str:
    def case_one_word(word) -> str:
        morph = pymorphy2.MorphAnalyzer()
        word = morph.parse(word)[0]
        try:
            return word.inflect(case).word
        except AttributeError:
            return word.word

    if len(text.split(' ')) > 1:
        return ' '.join(case_one_word(word) for word in text.split(' '))
    else:
        return case_one_word(text)


def agree_to_gender(word, to):
    morph = pymorphy2.MorphAnalyzer()

    to = [t for sub_word in to for t in morph.parse(sub_word) if t.tag.case == 'nomn']
    if len(to):
        to = to[0]

        res = [morph.parse(w)[0].inflect({to.tag.gender}).word for w in word.split(' ')]

        return ' '.join(res)

    warn('Не удалось просклонять слово "{word}" к "{to}"')
    return word


def names(args: List[_DBNamed]):
    if any(len(s.full_name()) > 25 for s in args):
        return ', '.join(s.short_name() for s in args)
    return ', '.join(s.full_name() for s in args)


def type_name(value: Any) -> str:
    if isinstance(value, type):
        if issubclass(value, _DBObject):
            return value.__type_name__
        else:
            return value.__name__
    if isinstance(value, _DBObject):
        return value.__type_name__
    if is_iterable(value):
        if len(value) > 0:
            if all(type(v) == type(value[0]) for v in value):
                if isinstance(value[0], _DBObject):
                    return value[0].__type_name__
                else:
                    return type(value[0]).__name__
            else:
                return ', '.join(type_name(v) for v in value)
        else:
            return '[]'

