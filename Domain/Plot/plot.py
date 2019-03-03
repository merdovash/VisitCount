from datetime import date
from typing import Callable, List

from matplotlib.axes import Axes, SubplotBase
from matplotlib.figure import Figure
from pandas import DataFrame, concat
from pandas._libs.tslibs.offsets import relativedelta

from DataBase2 import Lesson, Visitation, Student


def default_ax(fig: Figure, groups_count: int = 1) -> Axes:
    ax: Axes = fig.add_axes([0.06, 0.15, 0.90 if groups_count <= 4 else 0.70, 0.83])

    return ax


def post_ax(ax, groups_count=1):
    ax.grid(True)
    if groups_count > 4:
        ax.legend(bbox_to_anchor=(1, 1))


def prepare_data(user, semester, group_by: Callable[[Lesson], List]):
    lessons = Lesson.of(user)

    data = []
    year = None

    for lesson in lessons:
        if lesson.semester == semester and lesson.completed:
            year = lesson.date.year
            lesson_visitation = set(Visitation.of(lesson)) & set(Visitation.of(user))
            lesson_students = set(Student.of(lesson)) & set(Student.of(user))
            for item in list(set(group_by(lesson)) & set(group_by(user))):
                data.append([
                    len(set(Visitation.of(item)) & lesson_visitation),
                    len(set(Student.of(item)) & lesson_students),
                    lesson.date,
                    item.short_name(),
                    lesson.date.timetuple().tm_yday
                ])
    return data, year


def plot(user, semester, group_by: Callable[[Lesson], List], plot_type='distribution'):
    fig = Figure()
    # fig = Figure(figsize=(width, height), dpi=dpi, )
    data, year = prepare_data(user, semester, group_by)

    if len(data) == 0:
        return fig
    df = DataFrame(data)
    df.rename(index=str, columns={0: 'visit', 1: 'total', 2: 'date', 3: 'group_by', 4: 'day'}, inplace=True)
    df.sort_values('day', 0, inplace=True)

    if plot_type == 'distribution':

        visit = df.groupby(['group_by', 'day'])['visit'].sum().groupby(['group_by']).cumsum()
        total = df.groupby(['group_by', 'day'])['total'].sum().groupby(['group_by']).cumsum()
        res = DataFrame()
        res['rate'] = visit / total * 100
        grouped = res.groupby(['group_by'])

        ax = default_ax(fig, len(grouped.groups))

        for i, g in grouped:
            g = g.reset_index()
            g['day'] = g['day'].apply(lambda x: date(year, 1, 1) + relativedelta(days=x - 1))
            print(g)
            g.plot(x='day', y='rate', ax=ax, label=str(i), alpha=0.6)

        ax.set_ylim([-1, 101])
        ax.set_ylabel('Посещения, %')
        ax.set_xlabel('Дата')
        ax.tick_params(axis='x', rotation=30)

        post_ax(ax, len(grouped.groups))

    if plot_type == 'bar_week':
        df['week'] = df['date'].dt.week
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

        post_ax(ax, len(res.columns))

    if plot_type == 'bar_weekday':
        df['week_day'] = df['date'].dt.weekday
        print(df)
        visit = df.groupby(['group_by', 'week_day'])['visit'].sum()
        total = df.groupby(['group_by', 'week_day'])['total'].sum()

        res = DataFrame()
        res['rate'] = visit / total * 100
        res.reset_index(inplace=True)
        res.set_index(res['week_day'], inplace=True)

        res = res.pivot(columns='group_by', values='rate')
        print(res)
        ax = default_ax(fig, len(res.columns))
        res.plot.bar(ax=ax, alpha=0.7)

        # set ticks
        labels = ax.get_xticks().tolist()
        weekdays = 'пн.вт.ср.чт.пт.сб.вс'.split('.')
        for i in range(len(labels)):
            labels[i] = weekdays[labels[i]]

        ax.set_xticklabels(labels)
        ax.set_ylim([-1, 101])
        ax.set_ylabel('Посещения, %')
        ax.set_xlabel('День недели')

        post_ax(ax, len(res.columns))

    if plot_type == "bar_lesson":
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

        post_ax(ax, len(res.columns))

    if plot_type == 'hist':
        visit = df.groupby(['group_by'])['visit'].sum().groupby(['group_by']).cumsum()
        total = df.groupby(['group_by'])['total'].sum().groupby(['group_by']).cumsum()
        res = DataFrame()
        res['rate'] = visit / total * 100

        ax = default_ax(fig)

        res.hist(ax=ax, alpha=0.7, bins=25)

        ax.set_xlim([-1, 101])
        ax.set_ylabel('Количество')
        ax.set_xlabel('Посещения, %')

        post_ax(ax)

    if plot_type == 'total_alphabetic':
        visit = df.groupby(['group_by'])['visit'].sum().groupby(['group_by']).cumsum()
        total = df.groupby(['group_by'])['total'].sum().groupby(['group_by']).cumsum()
        res = DataFrame()
        res['rate'] = visit / total * 100
        res.reset_index(inplace=True)

        ax = default_ax(fig, len(res.groupby('group_by')))

        res.plot.bar(ax=ax, x='group_by', y='rate', alpha=0.7)

        ax.set_ylim([-1, 101])
        ax.set_ylabel('Посещения, %')

        post_ax(ax, len(res.groupby('group_by')))

    if plot_type == 'total_rated':
        visit = df.groupby(['group_by'])['visit'].sum().groupby(['group_by']).cumsum()
        total = df.groupby(['group_by'])['total'].sum().groupby(['group_by']).cumsum()
        res = DataFrame()
        res['rate'] = visit / total * 100
        res = res.reset_index().sort_values('rate', axis=0)

        ax = default_ax(fig, len(res.columns))

        res.plot.bar(ax=ax, x='group_by', y='rate', alpha=0.7)

        ax.set_ylim([-1, 101])
        ax.set_ylabel('Посещения, %')

    return fig

