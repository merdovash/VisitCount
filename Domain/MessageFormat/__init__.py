from enum import Enum
from warnings import warn

import pymorphy2


# noinspection NonAsciiCharacters
class Case(Enum):
    nomn = {'nomn'}
    gent = {'gent'}
    datv = {'datv'}
    accs = {'accs'}
    ablt = {'ablt'}
    loct = {'loct'}

    # русские варианты
    ИМЕНИТЕЛЬНЫЙ = {'nomn'}
    РОДИТЕЛЬНЫЙ = {'gent'}
    ДАТЕЛЬНЫЙ = {'datv'}
    ВИНИТЕЛЬНЫЙ = {'accs'}
    ТВОРИТЕЛЬНЫЙ = {'ablt'}
    ПРЕДЛОЖНЫЙ = {'loct'}



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