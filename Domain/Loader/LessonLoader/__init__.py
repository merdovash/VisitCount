import re
from collections import namedtuple
from datetime import datetime, timedelta
from typing import List, Tuple

from docx import Document

from DataBase2 import Professor, Session, Discipline, Group, Lesson, LessonsGroups
from Domain.Loader import WordReader


class LessonLoader:
    def get_disciplines(self):
        raise NotImplementedError()

    def get_lessons(self):
        raise NotImplementedError()

    def get_groups(self):
        raise NotImplementedError()


class WordLessonLoader(WordReader, LessonLoader):
    unit_regex = re.compile(
        r'(?:(?P<D>(?:[А-Яа-я\-A-Za-zё]*\s)+)\s*)'
        r'(?:\((?P<T>(?:(?:Лабораторная работа)|(?:Практические занятия)|(?:Лекция)))\)\s*)'
        r'(?:\((?:(?P<W>(?:[0-9]+(?:, )?)+) нед.)\)\s*)'
        r'(?:(?P<G>(?:[А-Яа-я]+-[0-9]+,? ?)+)\s*)'
        r'(?:ауд\.: ?(?P<R>[0-9]+(?:.*/[0-9]))\s*)'
    )

    start_time_regex = re.compile(
        r'(?:\d{1,2}[:.]\d{1,2})'
    )

    week_day = {
        ('понедельник',): 0,
        ('вторник',): 1,
        ('среда',): 2,
        ('четверг',): 3,
        ('пятница',): 4,
        ('суббота',): 5,
        ('воскресенье',): 6,
    }

    lesson_unit = namedtuple('lesson_unit', 'discipline type weeks weekday time groups room professor')

    def __init__(self, file, start_day: datetime, professor: Professor, session: Session):
        self.doc = Document(str(file))
        self.session = session
        self.professor = professor
        self.start_day = start_day
        lessons: List[Lesson] = []

        columns = {}

        rows = {}

        for table in self.doc.tables[0:1]:
            for row_index, row in enumerate(table.rows):
                for column_index, cell in enumerate(table.row_cells(row_index)):
                    if row_index == 0 and column_index == 0:
                        continue
                    elif row_index == 0:
                        columns[column_index] = self._week_day(cell.text)
                    elif column_index == 0:
                        rows[row_index] = self._time(cell.text)
                    else:
                        lessons_info: List[Tuple] = self.unit_regex.findall(cell.text)
                        for lesson_info in lessons_info:
                            for week in [int(i) for i in lesson_info[2].split(',')]:
                                discipline = Discipline.get_or_create(self.session,
                                                                      name=lesson_info[0].replace('\n', ''))

                                time = rows[row_index].split(':')
                                date = start_day + timedelta(week * 7 + columns[column_index],
                                                             int(time[0]) * 3600 + int(time[1]) * 60)
                                room = lesson_info[4]

                                lesson = Lesson.get_or_create(
                                    self.session,
                                    discipline=discipline,
                                    professor_id=professor.id,
                                    date=date
                                )
                                lesson.room_id = room
                                lesson.type = self._lesson_type(lesson_info[1])

                                for group_name in lesson_info[3].split(','):
                                    if group_name not in list(map(lambda x: x.name, lesson.groups)):
                                        lesson.groups.append(
                                            Group.get_or_create(self.session, name=group_name)
                                        )

                                session.flush()
                                lessons.append(lesson)
        self.lessons = lessons

    def _week_day(self, text):
        text = text.lower()
        for key in self.week_day.keys():
            if text in key:
                return self.week_day[key]

    def _time(self, text):
        return self.start_time_regex.findall(text)[0].replace('.', ':')

    def get_disciplines(self) -> List[Discipline]:
        return list(set(map(lambda x: x.discipline, self.lessons)))

    def get_groups(self) -> List[Group]:
        group_set = set()
        for lesson in self.lessons:
            for group in lesson.groups:
                group_set.add(group)
        return sorted(list(group_set), key=lambda x: x.name)

    def get_lessons(self) -> List[Lesson]:
        return self.lessons

    def _lesson_type(self, text):
        lower_text = text.lower()
        if "лекц" in lower_text:
            return Lesson.Type.Lecture
        if "лаб" in lower_text:
            return Lesson.Type.Lab
        if "практ" in lower_text:
            return Lesson.Type.Practice


if __name__ == '__main__':
    session = Session()
    professor = Professor.get_or_create(session, id=1)
    session.flush()
    d = WordLessonLoader("test1.docx", datetime(2019, 2, 11), professor, session)
    session.commit()
    lessons = session.query(Lesson).all()
    pass
