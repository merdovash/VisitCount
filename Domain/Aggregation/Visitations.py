from typing import List

from DataBase2 import Visitation, Lesson, Student


def all_visitations(students, lessons) -> List[Visitation]:
    return list(set(Visitation.of(students)) & set(Visitation.of(lessons)))


class VisitationRate:
    def __init__(self, visit, total):
        self.visit = visit
        self.total = total

    def rate(self, n=2):
        return round(self.visit / self.total, n) if self.total else 0


def visitations_rate(obj, semester=None):
    lessons = Lesson.of(obj, semester=semester)
    visit, total = 0, 0

    students_set = set(Student.of(obj))

    for lesson in lessons:
        total += len(set(Student.of(lesson)) & students_set)
        visit += len(all_visitations(students_set, lesson))

    return VisitationRate(visit, total)
