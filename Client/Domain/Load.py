from typing import Dict, Any

from DataBase2 import Update, Student, Professor, Discipline, Lesson, Group, students_groups, lessons_groups


def loads(data: Dict[str, Any]):
    rule = {
        'updates': Update,
        'students': Student,
        'professors': Professor,
        'disciplines': Discipline,
        'lessons': Lesson,
        'groups': Group,
        'students_groups': students_groups,
        'lessons_groups': lessons_groups
    }

    for key in data.keys():
        rule[key].loads(data[key])
