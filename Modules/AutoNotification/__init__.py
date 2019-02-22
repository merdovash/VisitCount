import threading
import time
from collections import defaultdict, namedtuple
from datetime import datetime, timedelta
from itertools import groupby
from pprint import pprint
from typing import List, Dict, Set, FrozenSet

from DataBase2 import Session, _DBEmailObject, Lesson, Discipline, Student, Visitation, Group

student_loss = namedtuple('student_loss', 'student loss total_lessons')


class MessageMaker():
    def __init__(self, reciever: _DBEmailObject):
        self.reciever = reciever
        if reciever.students_loss:
            self.prepare_students_loss()

    def prepare_students_loss(self):
        new_lessons_dict: Dict[Discipline, List[Lesson]] = defaultdict(list)
        lessons = Lesson.of(self.reciever)
        for lesson in lessons:
            if lesson.completed and lesson._updated >= self.reciever.last_auto:
                new_lessons_dict[lesson.discipline].append(lesson)

        bad_students: Dict[Discipline, List[student_loss]] = defaultdict(list)
        for discipline, new_lessons in new_lessons_dict.items():
            students: Set[Student] = set()
            for lesson in new_lessons:
                students.update(Student.of(lesson))

            for student in iter(students):
                all_lessons_by_discipline = list(filter(
                    lambda lesson: lesson.completed,
                    set(Lesson.of(student)) & set(Lesson.of(discipline))))
                all_visitation_by_discipline = list(
                    set(Visitation.of(Student)) & set(Visitation.of(all_lessons_by_discipline)))

                loss = len(all_lessons_by_discipline) - len(all_visitation_by_discipline)

                if loss > 2:
                    bad_students[discipline].append(student_loss(
                        student=student,
                        loss=loss,
                        total_lessons=len(all_lessons_by_discipline))
                    )
        message = ""
        for discipline, students in bad_students.items():
            message += f"<p>Дисциплина {discipline.full_name()}:</p>"

            students_grouped_by_group: Dict[FrozenSet[Group], List[Student]] = defaultdict(list)
            for student in students:
                students_grouped_by_group[frozenset(student.groups)].append(student)



    def send(self):
        print(self.reciever)


def init():
    def send(reciever: _DBEmailObject):
        sleep_until = reciever.last_auto + timedelta(0, 60 * 60 * reciever.interval_auto_hours)
        mm = MessageMaker(reciever)
        sleet_time = (sleep_until - datetime.now()).total_seconds()
        if sleet_time > 0:
            time.sleep(sleet_time)
        mm.send()

    def prepare(reciever: _DBEmailObject):
        now = datetime.now()
        if reciever.interval_auto_hours - (now - reciever.last_auto).total_seconds() <= 3600:
            sender = threading.Thread(target=send, args=(reciever,))
            sender.start()

    def look():
        while True:
            session = Session()
            stats = dict()
            search_start = datetime.now()
            for class_ in _DBEmailObject.email_subclasses():
                if len(class_.__subclasses__()) == 0:
                    items: List[_DBEmailObject] = session.query(class_).all()
                    stats[class_.__name__] = dict(total=0, prepared=[])
                    stats[class_.__name__]['total'] = len(items)
                    for item in items:
                        if item.auto:
                            stats[class_.__name__]['prepared'].append(item)
                            prepare(item)
            now = datetime.now()
            sleep = ((55 if now.minute < 55 else 115) - now.minute - 1) * 60 + (60 - now.second)
            pprint(stats)
            print(f'elapsed time on seek {(datetime.now() - search_start).total_seconds()}s.\n'
                  f'sleep for {sleep}s.')
            time.sleep(sleep)

    seeker = threading.Thread(target=look)
    seeker.start()


if __name__ == '__main__':
    init()
