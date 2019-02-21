from collections import defaultdict
from typing import List, Callable, Any

from pandas import DataFrame

from DataBase2 import Professor, Group, Lesson, Student, Visitation, Discipline, LessonsGroups
from Domain.Data import names_of_groups
from Domain.Structures import NamedVector
from Domain.functools.Decorator import memoize
from Domain.functools.Format import format_name


class Column:
    group_name = 'Группа'
    student_name = 'ФИО'
    date = 'Дата'
    type = 'Тип'
    discipline = 'Дисциплина'
    visit_rate = 'Посещения, %'
    visit_count = 'Количество посещений'
    student_count = 'Количество студентов'


class VisitationsRateByStudents:
    def __init__(self, lessons, groups=None):
        self.lessons = lessons
        self.groups = groups

        self.reset()

    def reset(self):
        self._data = list(self.lessons)
        return self

    def filter(self, func):
        self._data = [lesson for lesson in self._data if func(lesson)]
        return self

    def avg(self, group_by: Callable[[Lesson], Any]) -> dict:
        temp = defaultdict(list)

        students_by_groups = {}

        for lesson in self._data:
            if lesson.completed:
                if frozenset(lesson.groups) not in students_by_groups:
                    students = Student.of(lesson.groups)
                    if self.groups is not None:
                        students &= Student.of(self.groups)

                    students_by_groups[frozenset(lesson.groups)] = students

                temp[group_by(lesson)].append(
                    (len(Visitation.of(lesson) & Visitation.of(students_by_groups[frozenset(lesson.groups)])),
                     len(students_by_groups[frozenset(lesson.groups)])))
        res = {}
        for key in temp:
            acc = [0, 0]
            for visit_info in temp[key]:
                acc[0] += visit_info[0]
                acc[1] += visit_info[1]

            res[key] = acc[0] / acc[1] if acc[1] != 0 else 0

        return res


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

        data_frame = DataFrame(visit_rates,
                               columns=[Column.date, Column.type, Column.discipline, Column.visit_count,
                                        Column.student_count])
        return data_frame


class GroupAggregation:
    @staticmethod
    def by_professor(professor: Professor, html=False):
        assert isinstance(professor, Professor), f'object {professor} is not Professor'

        # список групп
        groups: List[Group] = professor.session() \
            .query(Group) \
            .join(LessonsGroups) \
            .join(Lesson) \
            .filter(Lesson.professor_id == professor.id) \
            .all()

        # список занятий по группам
        lessons: List[List[Lesson]] = list(map(lambda group: Lesson.of(group), groups))

        # количество студентов по группам
        students_count: List[int] = list(map(lambda group: len(Student.of(group)), groups))

        # сюда будут записаны процент посещений по группам
        data: List[float] = [-1 for _ in range(len(groups))]

        visits_count = 0
        total_count = 0

        for i, group in enumerate(groups):
            group_data = NamedVector(visit=0, total=0)
            for lesson in lessons[i]:
                if lesson.completed:
                    # посещение занятия группой находим как пересечение наборов посещений занятия и посещений группы
                    visits = len(set(Visitation.of(lesson)).intersection(set(Visitation.of(group))))
                    total = students_count[i]
                    group_data += NamedVector(visit=visits, total=total)

                    visits_count += visits
                    total_count += total
            else:
                data[i] = [NamedVector.rate(group_data.visit, group_data.total)]

        data_frame = DataFrame(data, index=list(map(lambda group: names_of_groups(group), groups)),
                               columns=['Посещения. %'])

        # итоговый процент посещений
        total = round(visits_count / total_count * 100, 2)

        if html:
            return total, data_frame.to_html()
        else:
            return total, data_frame


class DisciplineAggregator:
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

        data_frame = DataFrame(disciplines).T
        data_frame['Посещения, %'] = round(data_frame['visit'] / data_frame['total'] * 100, 1)

        data_frame = data_frame.drop(['visit', 'total'], axis=1)

        # data_frame[Column.discipline] = data_frame.index
        # data_frame = data_frame.reset_index()

        return data_frame[['Посещения, %', 'Всего занятий', 'Проведено занятий']]


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

        data_frame = DataFrame(data).T
        data_frame[Column.visit_rate] = round(data_frame[0].astype(float).divide(data_frame[1].astype(float)) * 100)
        data_frame = data_frame.rename(columns={2: 'Проведено занятий', 3: 'Всего занятий', 4: Column.date})
        data_frame = data_frame.loc[:, [Column.date, 'Проведено занятий', Column.visit_rate, 'Всего занятий']]
        data_frame[Column.visit_rate] = data_frame[Column.visit_rate].map(lambda x: 0 if x != x else x)

        return data_frame


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

            lesson_count = len(
                set(filter(lambda lesson: lesson.completed, Lesson.of(student))) & set(Lesson.of(professor)))
            visit_count = len(set(Visitation.of(student)) & set(Visitation.of(professor)))
            if lesson_count == 0:
                data[Column.visit_rate].append(0)
            else:
                data[Column.visit_rate].append(round(visit_count / lesson_count * 100) if lesson_count > 0 else 0)

        data_frame = DataFrame(data)

        return data_frame

    @staticmethod
    def by_discipline(disc):
        assert isinstance(disc, Discipline)

        data = {
            Column.student_name: [],
            Column.group_name: [],
            Column.visit_rate: []
        }

        for student in Student.of(disc):
            data[Column.student_name].append(format_name(student))
            data[Column.group_name].append(names_of_groups(Group.of(student)))

            lesson_count = len(set(filter(lambda lesson: lesson.completed, Lesson.of(student))) & set(Lesson.of(disc)))
            visit_count = len(set(Visitation.of(student)) & set(Visitation.of(disc)))

            if lesson_count:
                data[Column.visit_rate].append(round(visit_count / lesson_count * 100))
            else:
                data[Column.visit_rate].append(0)

        return DataFrame(data)
