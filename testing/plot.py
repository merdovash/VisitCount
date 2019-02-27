from collections import defaultdict
from datetime import datetime, timedelta, date
from typing import Any, Callable, List

from pandas import DataFrame
from pandas._libs.tslibs.offsets import relativedelta

from DataBase2 import Student, Lesson, Visitation
from Domain.Date import semester_start


def plot(user, ax, semester, group_by: Callable[[Lesson], List]):
    ax.cla()
    students = set(Student.of(user))
    lessons = Lesson.of(user)
    visitations = set(Visitation.of(user))

    data = []
    year = None

    for lesson in lessons:
        if lesson.semester == semester and lesson.completed:
            year = lesson.date.year
            lesson_visitation = set(Visitation.of(lesson))
            lesson_students = set(Student.of(lesson))
            for item in list(set(group_by(lesson)) & set(group_by(user))):
                data.append([
                    len(set(Visitation.of(item)) & lesson_visitation),
                    len(set(Student.of(item)) & lesson_students),
                    lesson.date,
                    str(item),
                    lesson.date.timetuple().tm_yday
                ])

    df = DataFrame(data)
    df.rename(index=str, columns={0: 'visit', 1: 'total', 2: 'date', 3: 'group_by', 4: 'day'}, inplace=True)
    df.sort_values('day', 0, inplace=True)
    visit = df.groupby(['group_by', 'day'])['visit'].sum()
    visit = visit.groupby(['group_by']).cumsum()
    total = df.groupby(['group_by', 'day'])['total'].sum().groupby(['group_by']).cumsum()
    res = DataFrame()
    res['rate'] = visit/total*100

    for i, g in res.groupby(['group_by']):
        g = g.reset_index()
        g['day'] = g['day'].apply(lambda x: date(year, 1, 1) + relativedelta(days=x - 1))
        g.plot(x='day', y='rate', ax=ax, label=str(i))


if __name__ == '__main__':
    plot(Student.get(id=22))
