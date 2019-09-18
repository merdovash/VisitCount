import re
from collections import namedtuple
from datetime import datetime, timedelta
from typing import List, Tuple, Dict

import xlrd
from docx import Document
from sqlalchemy import or_

from DataBase2 import Professor, Session, Discipline, Group, Lesson, Student, LessonType, LessonTypeSearchNames, Room, \
    Building, Semester
from DataBase2.SessionInterface import ISession
from Domain.Loader import WordReader, ExcelReader, Reader, PDFReader
from Domain.Validation.Values import Get


def get_lesson_by_time(day, time, start_day: datetime, professor: Professor, session: Session) -> Lesson:
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
    def __init__(self, session, semester: Semester):
        self._semester = semester
        self.session = session
        self._lesson_data = []
        self._groups = set()
        self._rooms = set()
        self._disciplines = set()
        self._lesson_types = set()
        self._professors = set()

    def get_disciplines(self):
        raise NotImplementedError()

    def get_lessons(self):
        raise NotImplementedError()

    def get_groups(self):
        raise NotImplementedError()

    def add_lesson_data(self, *, date: datetime, lesson_type: str, groups: List[str],
                        professor: List[str], discipline: str, room: List[str]):
        """
        
        :param date: 
        :param lesson_type: название типа занятия
        :param groups: список названий групп
        :param professor: Список ФИО; Если даны инициалы ИО, то присылать их без точек
        :param discipline: Название дисциплины
        :param room: пара (Здание, кабинет)
        :return: 
        """
        assert len(professor) in (2, 3)
        assert len(room) == 2
        self._lesson_data.append(
            dict(date=date, type=lesson_type, professor=professor, groups=groups, discipline=discipline, room=room))
        self._groups.union(set(groups))
        self._rooms.add(room)
        self._disciplines.add(discipline)
        self._lesson_types.add(lesson_type)
        self._professors.add(professor)

    def save(self):
        def load_professors() -> Dict[Tuple[str, str, str], Professor]:
            ps = dict()
            for p in self._professors:
                query = self.session.query(Professor).filter(Professor.last_name == p[0])
                if len(p[1]) > 1:
                    query.filter(Professor.first_name == p[1])
                else:
                    query.filter(Professor.first_name.like(f'{p[1]}%'))

                if len(p) == 3:
                    if len(p[2]) > 1:
                        query.filter(Professor.middle_name == p[2])
                    else:
                        query.filter(Professor.middle_name.like(f'{p[2]}%'))

                professor = query.all()
                if professor:
                    if len(professor) > 1:
                        professor = self._handle_multiple_professor_result(professor)
                        ps[p] = professor
                    else:
                        ps[p] = professor[0]
                else:
                    professor = Professor(last_name=p[0], first_name=p[1], middle_name=p[2] if len(p) == 3 else None)
                    self.session.add(professor)
                    ps[p] = professor
            return ps

        def load_disciplines() -> Dict[str, Discipline]:
            ds = dict()
            for d in self._disciplines:
                query = self.session.query(Discipline).filter(Discipline.name == d)

                discipline = query.all()
                if discipline:
                    if len(discipline) > 1:
                        discipline = self._handle_multiple_discipline_result(discipline)
                        ds[d] = discipline
                    else:
                        ds[d] = discipline[0]
                else:
                    discipline = Discipline(name=d)
                    session.add(discipline)
                    ds[d] = discipline

            return ds

        def load_lesson_types() -> Dict[str, LessonType]:
            lts = dict()

            for lt in self._lesson_types:
                query = self.session \
                    .query(LessonType) \
                    .join(LessonTypeSearchNames) \
                    .filter(LessonTypeSearchNames.search_name == lt.lower())

                lesson_type = query.first()
                if lesson_type:
                    lts[lt] = lesson_type
                else:
                    lesson_type = LessonType(name=lt)
                    self.session.add(lesson_type)
                    self.session.flush()
                    ltsn = LessonTypeSearchNames(search_name=lt)
                    self.session.add(ltsn)
                    ltsn.lesson_type = lesson_type
                    lts[lt] = LessonType
            return lts

        def load_groups() -> Dict[str, Group]:
            gs = dict()

            for g in self._groups:
                query = self.session.query(Group).filter(Group.name == g)

                group = query.all()
                if group:
                    if len(group) > 1:
                        group = self._handle_multiple_group_result(group)
                        gs[g] = group
                    else:
                        gs[g] = group[0]
                else:
                    group = Group(name=g)
                    session.add(group)
                    gs[g] = group

            return gs

        def load_room() -> Dict[Tuple[str, str], Room]:
            rs = dict()

            for r in self._rooms:
                query = self.session \
                    .query(Room) \
                    .join(Building) \
                    .filter(or_(Building.address == r[0], Building.abbreviation == r[0])) \
                    .filter(Room.room_number == r[1])

                room = query.all()
                if room:
                    if len(room) > 1:
                        room = self._handle_multiple_room_result(room)
                        rs[r] = room
                    else:
                        rs[r] = room[0]
                else:
                    room = Room(room_number=r[1])
                    session.add(room)
                    self.session.flush()
                    building = Building(address=r[0], abbreviation=r[0])
                    self.session.add(building)
                    room.building = building
                    rs[r] = room
            return rs

        professors = load_professors()
        disciplines = load_disciplines()
        lesson_types = load_lesson_types()
        groups = load_groups()
        rooms = load_room()

        self.session.flush()

        for ld in self._lesson_data:
            lesson = Lesson(date=ld['date'])
            lesson.professor = professors[ld['professor']]
            lesson.discipline = disciplines[ld['discipline']]
            lesson.room = rooms[ld['rooms']]
            lesson.groups.extend([groups[g] for g in ld['groups']])
            lesson.type = lesson_types[ld['lesson_type']]
            lesson.completed = False
            lesson.semester = self._semester

        self.session.flush()
        self.session.commit()

    def _handle_multiple_discipline_result(self, disciplines: List[Discipline]) -> Discipline:
        raise NotImplementedError("Необходимо определить что делать в случае если под описанную дисциплину "
                                  "подходит несколько записей")

    def _handle_multiple_professor_result(self, professors: List[Professor]) -> Professor:
        raise NotImplementedError("Необходимо определить что делать в случае если под описанного преподавателя "
                                  "подходит несколько записей")

    def _handle_multiple_group_result(self, group: List[Group]) -> Group:
        raise NotImplementedError("Необходимо определить что делать в случае если под описанную группу "
                                  "подходит несколько записей")


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
    DISCIPLINE_START_COL = 3
    DISCIPLINE_END_COL = 21

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

        discipline_regex = self._extract_discipline_name()
        if len(discipline_regex):
            discipline_name = discipline_regex[0]
            discipline = Discipline.get_or_create(self.session, name=discipline_name)
        else:
            raise ValueError('discipline is not found')

        self.students = list()
        for row in range(self.FULL_NAME_START_ROW, self.sheet.nrows):
            full_name = self.sheet.cell(row, self.FULL_NAME_COL).value
            if full_name not in [None, '']:
                student_regex = self.student_regex.findall(full_name)
                if len(student_regex):
                    student_regex = student_regex[0]
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
        lesson_type = LessonType.get_or_create(
            name='Практика',
            abbreviation='П',
            session=session)
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
                    continue
                    raise ValueError(f'{self.sheet.cell(self.DAY_ROW, col).value} is not acceptable date format')

                time_regex = self.day_regex.findall(self.sheet.cell(self.TIME_ROW, col).value)
                if len(time_regex):
                    time_regex = time_regex[0]
                    hours = int(time_regex[0])
                    minutes = int(time_regex[1])
                else:
                    raise ValueError(f'{self.sheet.cell(self.TIME_ROW, col).value} is not acceptable time format')

                time = datetime(start_day.year, month, day, hours, minutes)

                kwargs = dict(room_id='')
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
                lesson.type = lesson_type
                self.lessons.append(lesson)
            else:
                break

        self.discipline = discipline
        self.group = group
        self.session.commit()
        professor.session().expire_all()

    def _extract_discipline_name(self):
        for col in range(self.DISCIPLINE_START_COL, self.DISCIPLINE_END_COL):
            res = self.discipline_regex.findall(self.sheet.cell(0, col).value)
            if res:
                return res
        raise ValueError('Название дисциплины не найдено (ожидается, что оно находится в первой строке между '
                         'столбцами D и X)')

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


class PDFLessonLoader(LessonLoader, PDFReader):
    def __init__(self, session, semester):
        LessonLoader.__init__(self, session, semester)
        PDFReader.__init__(self)


if __name__ == '__main__':
    session = Session()
    # auth = Auth.log_in(login='VAE', password='123456')
    # professor = Professor.get_or_create(first_name='Валерий', last_name='Евстигнеев')

    # loader = ExcelLessonLoader('data.xls', datetime(2019, 9, 1, 0, 0, 0), professor, session)
    # loader = VisitationExcelLoader('data.xls', Group.get(id=1), Discipline.get(id=1), session)

    session.commit()
