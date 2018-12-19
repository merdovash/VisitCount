from typing import List

from pandas import DataFrame, np
from pandas.core.groupby import GroupBy

from DataBase2 import Professor, Group, Lesson, Student, Visitation, Discipline
from Domain.Data import names_of_groups
from Domain.functools.Decorator import memoize
from Domain.functools.Format import format_name
from Domain.functools.List import unique


class Column(object):
    group_name = 'Группа'
    student_name = 'ФИО'
    date = 'Дата'
    type = 'Тип'
    discipline = 'Дисциплина'
    visit_rate = 'Посещения, %'
    visit_count = 'Количество посещений'
    student_count = 'Количество студентов'


class Lessons:
    @staticmethod
    def by_professor(professor: Professor, groups=None, disciplines=None) -> DataFrame:
        assert isinstance(professor, Professor), f'object {professor} is not Professor'

        lessons = Lesson.of(professor)
        if groups is not None:
            lessons = list(set(lessons).intersection(set(Lesson.of(groups))))
        if disciplines is not None:
            lessons = list(set(lessons).intersection(set(Lesson.of(disciplines))))

        visit_rates = []
        for lesson in lessons:
            students = Student.of(lesson)
            if groups is not None:
                students = list(set(students).intersection(set(Student.of(groups))))

            visits = Visitation.of(lesson)
            if groups is not None:
                visits = list(set(visits).intersection(set(Visitation.of(students))))

            row = [
                lesson.date,
                lesson.type,
                lesson.discipline.name,
                len(visits),
                len(students)
            ]

            visit_rates.append(row)

        df = DataFrame(visit_rates,
                       columns=[Column.date, Column.type, Column.discipline, Column.visit_count, Column.student_count])
        return df


class GroupAggregation:
    @staticmethod
    def by_professor(professor: Professor, html=False):
        assert isinstance(professor, Professor), f'object {professor} is not Professor'

        # список групп
        groups: List[Group] = unique(Group.of(professor, flat_list=True))

        # список занятий по группам
        lessons: List[List[Lesson]] = list(map(lambda group: Lesson.of(group), groups))

        # количество студентов по группам
        students_count: List[int] = list(map(lambda group: len(Student.of(group)), groups))

        # сюда будут записаны процент посещений по группам
        data: List[float] = [-1 for _ in range(len(groups))]

        visits_count = 0
        total_count = 0

        for i, group in enumerate(groups):
            group_data = []
            for lesson in lessons[i]:
                if lesson.completed:
                    # посещение занятия группой находим как пересечение наборов посещений занятия и посещений группы
                    visits = len(set(Visitation.of(lesson)).intersection(set(Visitation.of(group))))
                    total = students_count[i]
                else:
                    visits = 0
                    total = 0

                group_data.append([visits, total])
                visits_count += visits
                total_count += total
            else:
                data[i] = [round(sum(map(lambda x: x[0], group_data)) / sum(map(lambda x: x[1], group_data)) * 100, 1)]

        df = DataFrame(data, index=list(map(lambda group: group.name, groups)), columns=['Посещения. %'])

        # итоговый процент посещений
        total = round(visits_count / total_count * 100, 2)

        print(df)

        if html:
            return total, df.to_html()
        else:
            return total, df


class DisciplineAggregation:
    @staticmethod
    def by_professor(professor: Professor) -> DataFrame:
        disciplines = {disc.name: {
            'Проведено занятий': 0,
            'Всего занятий': 0,
            'visit': 0,
            'total': 0,
            'Посещения, %': 0,
        } for disc in Discipline.of(professor)}

        lessons = Lesson.of(professor)

        for lesson in lessons:
            name = lesson.discipline.name
            if lesson.completed:
                disciplines[name]['total'] += len(Student.of(lesson))
                disciplines[name]['visit'] += len(Visitation.of(lesson))
                disciplines[name]['Проведено занятий'] += 1
            disciplines[name]['Всего занятий'] += 1

        df = DataFrame(disciplines).T
        df['Посещения, %'] = round(df['visit'] / df['total'] * 100, 1)

        df = df.drop(['visit', 'total'], axis=1)

        return df


class Weeks:
    @staticmethod
    @memoize
    def by_professor(professor: Professor, groups=None, disciplines=None) -> DataFrame:
        assert isinstance(professor, Professor), f'object {professor} is not Professor'

        df = Lessons.by_professor(professor, groups=groups, disciplines=disciplines)

        df[Column.date] = df[Column.date].apply(lambda date: date.isocalendar()[1])
        df[Column.date] = df[Column.date].apply(lambda date: 1 + date - df[Column.date].min())

        grouped: GroupBy = df.groupby(Column.date)

        grouped = grouped[Column.visit_count, Column.student_count].agg(np.sum)

        df = DataFrame(np.round(grouped[Column.visit_count] / grouped[Column.student_count], 2) * 100,
                       columns=[Column.visit_rate]).reset_index()

        return df


class WeekDaysAggregation:
    @staticmethod
    @memoize
    def by_professor(professor: Professor, groups=None, disciplines=None) -> DataFrame:
        assert isinstance(professor, Professor), f'object {professor} is not Professor'

        data = {0: [0, 0, 0, 0, 'Пн'],
                1: [0, 0, 0, 0, 'Вт'],
                2: [0, 0, 0, 0, 'Ср'],
                3: [0, 0, 0, 0, 'Чт'],
                4: [0, 0, 0, 0, 'Пт'],
                5: [0, 0, 0, 0, 'Сб'],
                6: [0, 0, 0, 0, 'Вс']}

        lessons = Lesson.of(professor)
        if groups is not None:
            lessons = list(set(lessons).intersection(set(Lesson.of(groups))))
        if disciplines is not None:
            lessons = list(set(lessons).intersection(set(Lesson.of(disciplines))))

        for lesson in lessons:
            week_day = lesson.date.weekday()
            # lesson count
            data[week_day][3] += 1

            if lesson.completed:
                # visit count
                visits = Visitation.of(lesson)
                if groups is not None:
                    visits = list(set(visits).intersection(set(Visitation.of(groups))))
                data[week_day][0] += len(visits)

                # student count
                students = Student.of(lesson)
                if groups is not None:
                    students = list(set(students).intersection(set(Student.of(groups))))
                data[week_day][1] += len(students)

                # completed lesson count
                data[week_day][2] += 1

        df = DataFrame(data).T
        df[Column.visit_rate] = round(df[0].astype(float).divide(df[1].astype(float)) * 100)
        df = df.rename(columns={2: 'Проведено занятий', 3: 'Всего занятий', 4: Column.date})
        df = df.loc[:, [Column.date, 'Проведено занятий', Column.visit_rate, 'Всего занятий']]
        df[Column.visit_rate] = df[Column.visit_rate].map(lambda x: 0 if x != x else x)

        return df


class StudentAggregator:
    @staticmethod
    def by_professor(professor):
        assert isinstance(professor, Professor)

        students = Student.of(professor)

        data = {
            Column.student_name: [],
            Column.group_name: [],
            Column.visit_rate: []
        }

        for student in students:
            data[Column.student_name].append(format_name(student))

            data[Column.group_name].append(names_of_groups(Group.of(student)))

            lesson_count = len(set(filter(lambda lesson:lesson.completed, Lesson.of(student))) & set(Lesson.of(professor)))
            visit_count = len(set(Visitation.of(student)) & set(Visitation.of(professor)))
            data[Column.visit_rate].append(round(visit_count/lesson_count*100))

        df = DataFrame(data)

        return df
