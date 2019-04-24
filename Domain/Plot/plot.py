from datetime import date
from math import floor
from typing import Callable, List, Type

import pandas
from matplotlib.axes import Axes, SubplotBase
from matplotlib.figure import Figure
from pandas import DataFrame, concat, Series
from pandas._libs.tslibs.offsets import relativedelta
import numpy as np
from scipy import stats
from scipy.optimize import curve_fit

from DataBase2 import Lesson, Visitation, Student, _DBObject, name, _DBRoot, Semester
from Domain.functools.Decorator import is_iterable
from Domain.functools.Format import names, agree_to_number, inflect, type_name


def gaussian(x, mean, amplitude=0., standard_deviation=1.):
    return amplitude * np.exp(- ((x - mean) / standard_deviation) ** 2)


def default_ax(fig: Figure, groups_count: int = 1) -> Axes:
    ax: Axes = fig.add_axes([0.06, 0.15, 0.90 if groups_count <= 4 else 0.70, 0.78])

    return ax


def post_ax(ax, groups_count=1, title='groups'):
    ax.grid(True)
    if groups_count > 4:
        ax.legend(bbox_to_anchor=(1, 1), title=title)
    else:
        ax.legend(title=title)


def rate(df: DataFrame, second_group_by: str = None):
    res = DataFrame()
    if second_group_by is not None:
        group = df.groupby(['group_by', second_group_by])
    else:
        group = df.groupby('group_by')
    res['rate'] = group.visit.sum() / group.total.sum()
    return res.reset_index()


def cumsum(df, second_group_by) -> DataFrame:
    visit = df.groupby(['group_by', second_group_by])['visit'].sum().groupby(['group_by']).cumsum()
    total = df.groupby(['group_by', second_group_by])['total'].sum().groupby(['group_by']).cumsum()
    res = DataFrame()
    res['rate'] = visit / total * 100
    return res


def prepare_data(root, semester, group_by: Type[_DBObject]):
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
                        'day': lesson.date.timetuple().tm_yday,
                        'week': lesson.week
                    })
    return data, year


def plot(user: List[_DBRoot], semester: List[Semester], group_by: Type[_DBRoot], plot_type: str = 'distribution'):
    fig = Figure()
    # fig = Figure(figsize=(width, height), dpi=dpi, )
    data, year = prepare_data(user, semester, group_by)

    title = None
    user_type = (type(user[0]) if is_iterable(user) else type(user))
    enable_group_by = user_type != group_by

    # тип исследуемых объектов
    type_description = agree_to_number(inflect(user_type.type_name, {"gent"}), len(user) if is_iterable(user) else 1)

    # имена исследуемых объектов
    user_names = name(user)
    if len(user_names) > 40:
        user_names = ""

    # описание группировок
    group_by_description = f"группированные по {agree_to_number(inflect(group_by.type_name, {'datv'}), 2)}" \
        if enable_group_by else ""

    # описание интервала
    interval_description = f'за {name(semester)}'

    if len(data) == 0:
        return fig
    df = DataFrame(data)
    df.sort_values('day', 0, inplace=True)

    if plot_type == 'distribution':
        title = 'Комулятивный уровень посещений всех занятий'
        res = cumsum(df, 'day')
        grouped = res.groupby(['group_by'])

        ax = default_ax(fig, len(grouped.groups))

        for i, g in grouped:
            g = g.reset_index()
            g['day'] = g['day'].apply(lambda x: date(year, 1, 1) + relativedelta(days=x - 1))
            g.plot(x='day', y='rate', ax=ax, label=str(i), alpha=0.6)

        ax.set_ylim([-1, 101])
        ax.set_ylabel('Посещения, %')
        ax.set_xlabel('Дата')
        ax.tick_params(axis='x', rotation=30)

        post_ax(ax, len(grouped.groups), type_name(user))

    elif plot_type == 'bar_week':
        title = 'Уровень посещений по неделям всех занятий'
        visit = df.groupby(['group_by', 'week'])['visit'].sum()
        total = df.groupby(['group_by', 'week'])['total'].sum()

        res = DataFrame()
        res['rate'] = visit / total * 100
        res.reset_index(inplace=True)
        res.set_index(res.week, inplace=True)

        res = res.pivot(columns='group_by', values='rate')

        ax = default_ax(fig, len(res.columns))

        res.plot.bar(ax=ax, alpha=0.7)

        ax.set_ylim([-1, 101])
        ax.set_ylabel('Посещения, %')
        ax.set_xlabel('Номер недели')

        post_ax(ax, len(res.columns), type_name(group_by))

    elif plot_type == 'bar_weekday':
        title = 'Уровень посещений по дням недели всех занятий'
        df['week_day'] = df['date'].dt.weekday
        visit = df.groupby(['group_by', 'week_day'])['visit'].sum()
        total = df.groupby(['group_by', 'week_day'])['total'].sum()

        res = DataFrame()
        res['rate'] = visit / total * 100
        res.reset_index(inplace=True)
        res.set_index(res['week_day'], inplace=True)

        res = res.pivot(columns='group_by', values='rate')
        res.sort_index(inplace=True)

        ax = default_ax(fig, len(res.columns))
        res.plot.bar(ax=ax, alpha=0.7)

        weekdays = 'пн.вт.ср.чт.пт.сб.вс'.split('.')
        ax.set_xticklabels([weekdays[i] for i in res.reset_index().week_day])
        ax.set_ylim([-1, 101])
        ax.set_ylabel('Посещения, %')
        ax.set_xlabel('День недели')

        post_ax(ax, len(res.columns), type_name(group_by))

    elif plot_type == "bar_lesson":
        title = f'Уровень посещений по времени занятия всех занятий'
        df['lesson'] = df['date'].dt.time
        visit = df.groupby(['group_by', 'lesson'])['visit'].sum()
        total = df.groupby(['group_by', 'lesson'])['total'].sum()

        res = DataFrame()
        res['rate'] = visit / total * 100
        res.reset_index(inplace=True)
        res.set_index(res['lesson'], inplace=True)
        res = res.pivot(columns='group_by', values='rate')

        ax = default_ax(fig, len(res.columns))

        res.plot.bar(ax=ax, alpha=0.7)

        ax.set_ylabel('Посещения, %')
        ax.set_xlabel('Занятие')

        post_ax(ax, len(res.columns), type_name(group_by))

    elif plot_type == 'hist':
        title = "Вероятности уровня посещений для"
        visit = df.groupby(['group_by'])['visit'].sum().groupby(['group_by']).cumsum()
        total = df.groupby(['group_by'])['total'].sum().groupby(['group_by']).cumsum()
        res = DataFrame()
        res['rate'] = visit / total * 100

        ax = default_ax(fig)

        bin_heights, bin_borders, _ = ax.hist(res.rate, alpha=0.7, bins=50, label='Гистограма', density=True)

        xt = ax.get_xticks()
        xmin, xmax = min(xt), max(xt)
        lnspc = np.linspace(xmin, xmax, res.shape[0])

        m, s = stats.norm.fit(res.rate)  # get mean and standard deviation
        pdf_g = stats.norm.pdf(lnspc, m, s)  # now get theoretical values in our interval
        ax.plot(lnspc, pdf_g, label="Norm")  # plot it

        ag, bg, cg = stats.gamma.fit(res.rate)
        pdf_gamma = stats.gamma.pdf(lnspc, ag, bg, cg)
        ax.plot(lnspc, pdf_gamma, label="Gamma")

        ax.set_xlim([-1, 101])
        ax.set_ylabel(f'Вероятность (из {len(res)})')
        ax.set_xlabel('Посещения, %')
        ax.legend()

        post_ax(ax, 1, type_name(group_by))

    elif plot_type == 'total_alphabetic':
        title = f'Уровень посещений всех занятий'
        visit = df.groupby(['group_by', 'user'])['visit'].sum().groupby(['group_by']).cumsum()
        total = df.groupby(['group_by', 'user'])['total'].sum().groupby(['group_by']).cumsum()
        res = DataFrame()
        res['rate'] = visit / total * 100
        res.reset_index(inplace=True)

        ax = default_ax(fig, len(res.groupby('group_by')))
        res = res.pivot(index='user', columns='group_by', values='rate')
        res.plot.bar(ax=ax, alpha=0.7)

        ax.set_ylim([-1, 101])
        ax.set_ylabel('Посещения, %')
        ax.set_xlabel(type_name(user))

        post_ax(ax, res.shape[1], type_name(group_by))

    elif plot_type == 'total_rated':
        title = "Уровень посещений всех занятий "
        visit = df.groupby(['group_by', 'user'])['visit'].sum().groupby(['group_by']).cumsum()
        total = df.groupby(['group_by', 'user'])['total'].sum().groupby(['group_by']).cumsum()
        res = DataFrame()
        res['rate'] = visit / total * 100
        res = res.reset_index()

        ax = default_ax(fig, len(res.columns))

        if enable_group_by:
            res = res.pivot(index='user', columns='group_by', values='rate')
            res = res.reindex(res.mean().sort_values(ascending=False).index, axis=1)
            res.plot.bar(ax=ax, alpha=0.7, width=0.99, align='center')
        else:
            res = res.sort_values(by='rate')
            res.plot.bar(ax=ax, x='user', y='rate')

        ax.set_ylim([-1, 101])
        ax.set_ylabel('Посещения, %')
        ax.set_xlabel(f'{type_name(user)} по возрастанию посещаемости')
        post_ax(ax, 1, type_name(group_by))

    elif plot_type == 'scatter':
        title = 'Уровень посещений всех занятий'
        group = df.groupby(['group_by'])
        res = DataFrame()
        res['rate']: DataFrame = group.visit.sum() / group.total.sum() * 100
        res.sort_values('rate', inplace=True)
        res.reset_index(inplace=True)
        res.index.name = 'index'
        res.reset_index(inplace=True)
        res.index = res.index + 1

        params = np.polyfit(res.index, res.rate, 2)
        trend = DataFrame()
        trend['x'] = np.linspace(0, res.shape[0], res.shape[0])
        trend['y'] = np.polyval(params, trend['x'])

        ax = default_ax(fig, 1)

        res.plot.scatter(x='index', y='rate', ax=ax)
        trend.plot(x='x', y='y', ax=ax, label='Линия тренда')
        ax.set_ylim([-1, 101])
        ax.set_ylabel('Посещения, %')
        ax.set_xlabel('Студенты (по возрастанию посещаемости)')

    elif plot_type == 'deviation':
        title = "Изменение уровня посещений с течением времени для"
        res = cumsum(df, 'day')
        grouped = res.groupby(['group_by'])

        ax = default_ax(fig, len(grouped.groups))

        for i, g in grouped:
            g = g.reset_index()
            g['day'] = g['day'].apply(lambda x: date(year, 1, 1) + relativedelta(days=x - 1))
            g.rate = g.rate.pct_change()
            g = g.fillna(0)

            g.plot(x='day', y='rate', ax=ax, label=str(i), alpha=0.6)

        # ax.set_ylim([-1, 1])
        ax.set_ylabel('Изменение уровня посещения, %')
        ax.set_xlabel('Дата')
        ax.tick_params(axis='x', rotation=30)

        post_ax(ax, len(grouped.groups), type_name(group_by))

    else:
        raise ValueError(f'no such plot type "{plot_type}"')

    ax.set_title(' '.join((title, type_description, user_names, group_by_description, interval_description)),
                 {'fontsize': 11})

    return fig
