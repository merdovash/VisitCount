from typing import List

from DataBase2 import Visitation


def all_visitations(students, lessons)->List[Visitation]:
    return list(set(Visitation.of(students)) & set(Visitation.of(lessons)))
