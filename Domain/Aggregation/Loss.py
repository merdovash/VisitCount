from datetime import datetime

from Domain.Aggregation.Lessons import intersect_lessons_of, divide_by_date
from Domain.Aggregation.Visitations import all_visitations


def student_loss(student, discipline=None, professor=None, last_date=datetime.now(),
                 max_available_loss=3) -> int or None:
    lessons = intersect_lessons_of(student, discipline, professor)

    completed_lesson = [lesson for lesson in lessons if lesson.completed]

    old_lessons, new_lessons = divide_by_date(completed_lesson, last_date)

    new_visitations = all_visitations(student, new_lessons)
    old_visitations = all_visitations(student, old_lessons)
    lost_lesson = len(completed_lesson) - (len(new_visitations) + len(old_visitations))
    if lost_lesson >= max_available_loss and len(new_visitations) < len(new_lessons):
        return lost_lesson

    return None
