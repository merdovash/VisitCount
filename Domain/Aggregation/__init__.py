from pandas import DataFrame

from DataBase2 import Professor, Group, Lesson, Student, Visitation


class GroupAggregation:
    @staticmethod
    def by_professor(professor: Professor, html=False):
        assert isinstance(professor, Professor), f'object {professor} is not Professor'

        groups = Group.of(professor, flat_list=True)

        lessons = list(map(lambda group: Lesson.of(group), groups))

        data = [None for _ in range(len(groups))]

        students_count = list(map(lambda group: len(Student.of(group)), groups))
        visits_count = [None for _ in range(len(groups))]

        for i, group in enumerate(groups):
            visits_count[i] = len(Visitation.of(lessons))
            data[i] = [round(visits_count[i] / students_count[i], 2)]

        df = DataFrame(data, index=list(map(lambda group: group.name, groups)), columns=['Посещения. %'])

        total = round(sum(visits_count) / sum(students_count), 2)

        if html:
            return total, df.to_html()
        else:
            return total, df
