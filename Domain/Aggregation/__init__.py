from pandas import DataFrame, np
from pandas.core.groupby import GroupBy

from DataBase2 import Professor, Group, Lesson, Student, Visitation
from Domain.functools.List import unique


class Column(object):
    date = 'Дата'
    type = 'Тип'
    discipline = 'Дисциплина'
    visit_rate = 'Посещения, %'
    visit_count = 'Количество посещений'
    student_count = 'Количество студентов'


class Lessons:
    @staticmethod
    def by_professor(professor: Professor) -> DataFrame:
        assert isinstance(professor, Professor), f'object {professor} is not Professor'

        visit_rates = [
            [
                lesson.date,
                lesson.type,
                lesson.discipline.name,
                len(Visitation.of(lesson)),
                len(Student.of(lesson))
            ]
            for lesson in Lesson.of(professor)]

        df = DataFrame(visit_rates,
                       columns=[Column.date, Column.type, Column.discipline, Column.visit_count, Column.student_count])

        return df


class GroupAggregation:
    @staticmethod
    def by_professor(professor: Professor, html=False):
        assert isinstance(professor, Professor), f'object {professor} is not Professor'

        groups = unique(Group.of(professor, flat_list=True))

        lessons = list(map(lambda group: Lesson.of(group), groups))

        data = [-1 for _ in range(len(groups))]

        students_count = list(map(lambda group: len(Student.of(group)), groups))
        visits_count = [-1 for _ in range(len(groups))]

        for i, group in enumerate(groups):
            visits_count[i] = len(Visitation.of(lessons))
            data[i] = [round(visits_count[i] / students_count[i], 2)]

        df = DataFrame(data, index=list(map(lambda group: group.name, groups)), columns=['Посещения. %'])

        total = round(sum(visits_count) / sum(students_count), 2)

        if html:
            return total, df.to_html()
        else:
            return total, df


class Weeks:
    @staticmethod
    def by_professor(professor: Professor) -> DataFrame:
        assert isinstance(professor, Professor), f'object {professor} is not Professor'

        df = Lessons.by_professor(professor)

        df[Column.date] = df[Column.date].apply(lambda date: date.isocalendar()[1])
        df[Column.date] = df[Column.date].apply(lambda date: 1 + date - df[Column.date].min())

        grouped: GroupBy = df.groupby(Column.date)

        grouped = grouped[Column.visit_count, Column.student_count].agg(np.sum)

        df = DataFrame(np.round(grouped[Column.visit_count] / grouped[Column.student_count], 2) * 100,
                       columns=[Column.visit_rate]).reset_index()

        print(df)

        return df


class WeekDays:
    @staticmethod
    def by_professor(professor: Professor) -> DataFrame:
        assert isinstance(professor, Professor), f'object {professor} is not Professor'

        df = Lessons.by_professor(professor)

        df[Column.date] = df[Column.date].apply(lambda date: date.isoweekday())

        grouped: GroupBy = df.groupby(Column.date)

        grouped = grouped[Column.visit_count, Column.student_count].agg(np.sum)

        df = DataFrame(np.round(grouped[Column.visit_count] / grouped[Column.student_count], 2) * 100,
                       columns=[Column.visit_rate]).reset_index()

        print(df)

        return df
