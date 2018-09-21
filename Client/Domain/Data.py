from itertools import chain
from typing import List


def students_of_groups(groups: List['Group']):
    return sorted(chain.from_iterable(map(lambda x: x.students, chain(groups))), key=lambda x: x.last_name)
