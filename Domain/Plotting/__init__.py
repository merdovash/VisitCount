import sys
from datetime import date
from typing import Type, List

from PyQt5.QtWidgets import QApplication
from pandas import DataFrame
from pandas._libs.tslibs.offsets import relativedelta

from DataBase2 import Group, Discipline, Semester, _DBRoot, Semester, Lesson, Visitation, Student, _DBObject
from Domain.functools.Decorator import is_iterable
from Domain.functools.Format import inflect, agree_to_number, names


class PlotInfo:
    def __init__(self, data, x, y, x_axis_label, y_axis_label, title, plot_type, legend, **kwargs):
        self.data = data
        self.legend = legend
        self.x = x
        self.y = y
        self.x_axis_label = x_axis_label
        self.y_axis_label = y_axis_label
        self.plot_type = plot_type
        self.title = title

    def create(self):
        raise NotImplementedError()

    def widget(self):
        raise NotImplementedError()

    @classmethod
    def prepare_data(cls, root, semester, group_by: Type[_DBObject]):
        data = []
        year = None
        for user in root:
            user_name = user.short_name()
            lessons = Lesson.of(user)

            groups = set(group_by.of(user))

            for lesson in lessons:
                if (lesson.semester == semester or (isinstance(semester, (set, list)) and lesson.semester in semester)) \
                        and lesson.completed:
                    year = lesson.date.year
                    lesson_visitation = set(Visitation.of(lesson)) & set(Visitation.of(user))
                    lesson_students = set(Student.of(lesson)) & set(Student.of(user))
                    for item in list(set(group_by.of(lesson)) & groups):
                        data.append({
                            'user': user_name,
                            'visit': len(set(Visitation.of(item)) & lesson_visitation),
                            'total': len(set(Student.of(item)) & lesson_students),
                            'date': lesson.date,
                            'group_by': item.short_name(),
                            'day': lesson.date.date(),
                            'week': lesson.week
                        })
        return data, year

    @classmethod
    def cumsum(cls, df, second_group_by) -> DataFrame:
        visit = df.groupby(['group_by', second_group_by])['visit'].sum().groupby(['group_by']).cumsum()
        total = df.groupby(['group_by', second_group_by])['total'].sum().groupby(['group_by']).cumsum()
        res = DataFrame()
        res['rate'] = visit / total * 100
        return res

    @classmethod
    def make_title(cls, user, group, labels):
        user_type = user[0] if is_iterable(user) else user

        title = "Комулятивный уровень посещений всех занятий {} {}".format(
            agree_to_number(inflect(type(user_type).type_name, {"gent"}), len(user) if is_iterable(user) else 1),
            names(user) if type(user[0]) != group else "",
        )
        if group != user_type:
            title += " сгруппированные по {} [{}].".format(
               inflect(agree_to_number(group.type_name, len(labels)), {'datv'}),
                ', '.join(labels)
            )
        return title

    @classmethod
    def distribution(cls, user: List[_DBRoot], group: Type[_DBRoot], semester: List[Semester]) -> 'PlotInfo':
        data, year = cls.prepare_data(user, semester, group)
        df = DataFrame(data)
        df.sort_values('day', 0, inplace=True)
        res = cls.cumsum(df, 'day')
        grouped = res.groupby(['group_by'])

        res = []
        legend = []
        for i, g in grouped:
            g = g.reset_index()
            # g['day'] = g['day'].apply(lambda x: date(year, 1, 1) + relativedelta(days=x - 1))
            res.append(g)
            legend.append(i)

        return cls(
            data=res,
            x='day',
            y='rate',
            title=cls.make_title(user, group, legend),
            x_axis_label='Дата',
            y_axis_label='Процент посещений',
            legend=legend,
            plot_type='distribution'
        )
