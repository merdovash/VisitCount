from typing import Sequence, List

from DataBase2 import Lesson, _DBObject


def intersect_lessons_of(*args: Sequence[_DBObject])-> List[Lesson]:
    res = set()
    if len(args) > 0:
        res = set(Lesson.of(args[0]))
        for arg in args[1:]:
            if arg is not None:
                res &= set(Lesson.of(arg))
    return list(res)


def divide_by_date(lessons, date):
    before = []
    after = []
    for lesson in lessons:
        if lesson._created and lesson._created>date:
            after.append(lesson)
        elif lesson._updated and lesson._updated>date:
            after.append(lesson)
        else:
            before.append(lesson)

    return before, after
