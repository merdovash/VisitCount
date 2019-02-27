import re
from collections import namedtuple
from datetime import datetime, timedelta
from typing import List, Tuple

import xlrd
from docx import Document

from DataBase2 import Professor, Session, Discipline, Group, Lesson, Student
from DataBase2.SessionInterface import ISession
from Domain.Loader import WordReader, ExcelReader, Reader
from Domain.Validation.Values import Get


def get_lesson_by_time(day, time, start_day: datetime, professor: Professor, session: Session)-> Lesson:
    day_regex = re.compile(
        r'(?:(?P<month>[0-9]+)[:.](?P<day>[0-9]+))'
    )

    date_regex = day_regex.findall(day)
    if len(date_regex):
        date_regex = date_regex[0]
        month = int(date_regex[1])
        day = int(date_regex[0])
    else:
        raise ValueError(f'{day} is not acceptable date format')

    time_regex = day_regex.findall(time)
    if len(time_regex):
        time_regex = time_regex[0]
        hours = int(time_regex[0])
        minutes = int(time_regex[1])
    else:
        raise ValueError(f'{time} is not acceptable time format')

    time = datetime(start_day.year, month, day, hours, minutes)

    return Lesson.get(session, time=time, professor_id=professor.id)


class LessonLoader(Reader):
    def get_disciplines(self):
        raise NotImplementedError()

    def get_lessons(self):
        raise NotImplementedError()

    def get_groups(self):
        raise NotImplementedError()


class ExcelLessonLoader(ExcelReader, LessonLoader):
    group_regex = re.compile(
        r'(?:(?:[Гг]рупп[аы])?\s?(?P<G>(?:[А-Яа-я]+-[0-9]+,?\s?)+))'
    )

    discipline_regex = re.compile(
        r'(?:(?:[Дд]исциплина\s?:?\s)?(?P<discipline>.+))'
    )

    student_regex = re.compile(
        r'(?:(?P<last>[А-яа-яё]+) (?P<first>[А-яа-яё]+)(?: (?P<middle>[А-яа-яё]+))?)'
    )

    day_regex = re.compile(
        r'(?:(?P<month>[0-9]+)[:.](?P<day>[0-9]+))'
    )

    INDEX_COL = 0
    CARD_COL = 1
    FULL_NAME_COL = 2
    TIME_START_COL = 3

    GROUP_CELL = (0, 2)
    DISCIPLINE_CELL = (0, 3)

    FULL_NAME_START_ROW = 5
    LESSON_INDEX_ROW = 1
    WEEK_ROW = 2
    DAY_ROW = 3
    TIME_ROW = 4

    def __init__(self, file: str, start_day: datetime, professor: Professor, session: ISession):
        self.document = xlrd.open_workbook(filename=file)
        self.sheet = self.document.sheet_by_index(0)

        self.session: ISession = session

        group_regex = self.group_regex.findall(self.sheet.cell(*self.GROUP_CELL).value)
        if len(group_regex):
            group_name = group_regex[0]
            group = Group.get_or_create(self.session, name=group_name)
        else:
            raise ValueError('group is not found')

        discipline_regex = self.discipline_regex.findall(self.sheet.cell(*self.DISCIPLINE_CELL).value)
        if len(discipline_regex):
            discipline_name = discipline_regex[0]
            discipline = Discipline.get_or_create(self.session, name=discipline_name)
        else:
            raise ValueError('discipline is not found')

        self.students = list()
        for row in range(self.FULL_NAME_START_ROW, self.sheet.nrows):
            full_name = self.sheet.cell(row, self.TIME_START_COL).value
            if full_name not in [None, '']:
                student_regex = self.student_regex.findall(full_name)
                if len(student_regex):
                    if len(student_regex) == 2:
                        student = Student.get_or_create(self.session,
                                                        last_name=student_regex[0],
                                                        first_name=student_regex[1])
                    else:
                        student = Student.get_or_create(self.session,
                                                        last_name=student_regex[0],
                                                        first_name=student_regex[1],
                                                        middle_name=student_regex[2])
                    if student.id is None:
                        student.groups.append(group)

                    card_id = Get.card_id(self.sheet.cell(row, self.CARD_COL).value)
                    if card_id not in [None, ''] and card_id != student.card_id:
                        student.card_id = card_id

                    self.students.append(student)
            else:
                break

        self.lessons = list()
        for col in range(self.TIME_START_COL, self.sheet.ncols):
            lesson_index = self.sheet.cell(self.LESSON_INDEX_ROW, col).value
            if lesson_index not in [None, '']:
                date_regex = self.day_regex.findall(self.sheet.cell(self.DAY_ROW, col).value)
                if len(date_regex):
                    date_regex = date_regex[0]
                    month = int(date_regex[1])
                    day = int(date_regex[0])
                else:
                    raise ValueError(f'{self.sheet.cell(self.DAY_ROW, col).value} is not acceptable date format')

                time_regex = self.day_regex.findall(self.sheet.cell(self.TIME_ROW, col).value)
                if len(time_regex):
                    time_regex = time_regex[0]
                    hours = int(time_regex[0])
                    minutes = int(time_regex[1])
                else:
                    raise ValueError(f'{self.sheet.cell(self.TIME_ROW, col).value} is not acceptable time format')

                time = datetime(start_day.year, month, day, hours, minutes)

                kwargs = dict(room_id='', type=Lesson.Type.Practice)
                if discipline.id is None:
                    lesson = Lesson.new(self.session, date=time, professor_id=professor.id, **kwargs)
                    lesson.discipline = discipline
                    lesson.groups.append(group)
                else:
                    lesson = Lesson.get_or_create(
                        self.session,
                        date=time,
                        professor_id=professor.id,
                        discipline_id=discipline.id,
                        **kwargs)
                    if group not in lesson.groups:
                        lesson.groups.append(group)
                self.lessons.append(lesson)
            else:
                break

        self.discipline = discipline
        self.group = group
        self.session.commit()
        professor.session().expire_all()

    def get_disciplines(self):
        return [self.discipline]

    def get_lessons(self):
        return self.lessons

    def get_groups(self):
        return [self.group]


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

