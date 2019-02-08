from collections import namedtuple
from typing import Callable

import xlrd
from PyQt5.QtCore import QObject
from PyQt5.QtWidgets import QMessageBox, QApplication

from Client.MyQt.Window.interfaces import IDataBaseUser
from DataBase2 import Group, Lesson, Professor, LessonsGroups, Student, Visitation
from Domain.functools.Decorator import memoize, safe
from Domain.functools.List import find

student_info = namedtuple('student_info', 'row card_id name visitations real_student')
lesson_info = namedtuple('lesson_info', 'col month day hour minute real_lesson')
visit_info = namedtuple('visit_info', 'col row status')


class Reader(IDataBaseUser, QObject):
    students_row = 5

    date_row = 3
    time_row = 4

    card_id_col = 1
    name_col = 2
    body_start_col = 3

    group_name_index = (0, 2)

    def __init__(self, file, professor, progress_bar=None,
                 on_warning=lambda x: None,
                 on_finish=lambda x: None,
                 on_error=lambda x: None):
        IDataBaseUser.__init__(self)
        QObject.__init__(self)

        book = xlrd.open_workbook(file.toLocalFile())
        self.sheet = book.sheet_by_index(0)

        self.progress_bar = progress_bar

        self.professor = professor
        print(self.cell(*Reader.group_name_index).split('. ')[1].split(', '))
        self.group = self.session \
            .query(Group) \
            .filter(Group.name.in_(self.cell(*Reader.group_name_index).split('. ')[1].replace(' ', '').split(','))) \
            .all()

        self.lesson = self.session \
            .query(Lesson) \
            .join(Professor) \
            .join(LessonsGroups) \
            .filter(Professor.id == self.professor.id) \
            .filter(LessonsGroups.group_id.in_([group.id for group in self.group])) \
            .all()

        self.student = Student.of(self.group)

        self.on_warning = on_warning
        self.on_finish = on_finish
        self.on_error = on_error

        self.current = 0

    def cell(self, row, col):
        return self.sheet.cell(row, col).value

    def on_error(self, msg):
        QMessageBox.critical(QWidget=self, p_str=msg)

    def on_warning(self, msg):
        QMessageBox.information(QWidget=self, p_str=msg)

    def on_finish(self, msg):
        QMessageBox.information(QWidget=self, p_str=msg)

    @memoize
    def students(self):
        def real_student_finder(name):
            name = name.split(' ')
            if len(name) == 3:
                return lambda student: student.last_name == name[0] and student.first_name == name[1] and \
                                       student.middle_name == name[2]
            elif len(name) == 2:
                return lambda student: student.last_name == name[0] and student.first_name == name[1]

            elif len(name) == 4 and (name[3] == "*" or name[3] == "**"):
                return lambda student: student.last_name == name[0] and student.first_name == name[1] and \
                                       student.middle_name == name[2]

            else:
                raise NotImplementedError()

        l = []
        for row in range(Reader.students_row, self.sheet.nrows):
            QApplication.processEvents()
            if self.sheet.cell(row, 0).value is not None and self.sheet.cell(row, 0).value != "":
                name = self.cell(row, Reader.name_col)

                try:
                    card_id = int(self.cell(row, Reader.card_id_col))
                except ValueError:
                    self.on_error(
                        f'В строке {row + 1} невозможно прочитать идентификтаор карты. Строка будет пропущена.')
                    continue

                l.append(
                    student_info(
                        row=row,
                        card_id=card_id,
                        name=name,
                        visitations=self.visitations(row),
                        real_student=find(real_student_finder(name), self.student)
                    )
                )
        return l

    def visitations(self, row):
        l = []
        for col in range(Reader.body_start_col, len(list(self.lessons())) + Reader.body_start_col):
            l.append(visit_info(col=col,
                                row=row,
                                status=self.cell(row, col) == 1))

        return l

    @memoize
    def lessons(self):
        l = []
        for col in range(Reader.body_start_col, self.sheet.ncols):
            QApplication.processEvents()
            if self.cell(self.date_row, col) not in [None, ''] and self.cell(self.time_row, col) not in [None, '']:
                try:
                    minute = int(self.cell(self.time_row, col).split(':')[1])
                except IndexError:
                    self.on_warning(f'В столбце {col + 1}, строке {self.time_row + 1} неправильный формат времени')
                    continue

                try:
                    hour = int(self.cell(self.time_row, col).split(':')[0])
                except IndexError:
                    self.on_warning(f'В столбце {col + 1}, строке {self.time_row + 1} неправильный формат времени')
                    continue

                try:
                    day = int(self.cell(self.date_row, col).split('.')[0])
                except IndexError:
                    self.on_warning(f'В столбце {col + 1}, строке {self.date_row + 1} неправильный формат даты')
                    continue

                try:
                    month = int(self.cell(self.date_row, col).split('.')[1])
                except IndexError:
                    self.on_warning(f'В столбце {col + 1}, строке {self.date_row + 1} неправильный формат даты')
                    continue

                l.append(
                    lesson_info(
                        col=col,
                        month=month,
                        day=day,
                        hour=hour,
                        minute=minute,
                        real_lesson=find(lambda x: x.date.hour == hour and x.date.minute == minute and
                                                   x.date.month == month and x.date.day == day, self.lesson)
                    )
                )
            else:
                break
        return l

    @safe
    def run(self, callback: Callable[[int], None]):
        STAGE = 0

        STAGE_RATE = [0.25, 0.75]
        assert sum(STAGE_RATE) == 1

        # LESSON STAGE
        lessons = self.lessons()
        count = len(lessons)
        for index, lesson in enumerate(lessons):
            QApplication.processEvents()
            callback(int(100 * (sum(STAGE_RATE[:STAGE]) + STAGE_RATE[STAGE] * (index / count))))

            if lesson.real_lesson is not None:
                lesson.real_lesson.completed = True
            else:
                self.on_warning(f'Для столбца {lesson.col} не найдено занятияе в БД. Столбец будет пропущен при '
                                f'записи.\nИзмените дату занятия в программе или в файле и повторите попытку ('
                                f'дупликаты записей будут проигнорированы).')
        else:
            STAGE += 1

        # STUDENT STAGE
        visitations = []
        count = len(self.students())
        for index, student in enumerate(self.students()):
            QApplication.processEvents()
            callback(int(100 * (sum(STAGE_RATE[:STAGE]) + STAGE_RATE[STAGE] * (index / count))))

            if student.real_student is not None:

                if student.real_student.card_id != student.card_id:
                    student.real_student.card_id = student.card_id

                for visit in student.visitations:
                    QApplication.processEvents()
                    if visit.status:
                        lesson = find(lambda x: x.col == visit.col, lessons)
                        if lesson is not None:
                            real_lesson = lesson.real_lesson
                            if real_lesson is not None:
                                Visitation.get_or_create(
                                    session=self.professor.session(),
                                    student_id=student.real_student.id,
                                    lesson_id=lesson.real_lesson.id)
                        else:
                            n = '\n'
                            self.on_warning(f"Не удалось найти {visit} в {n.join([str(l) for l in lessons])}")

            else:
                self.on_error(f'Студент {student.name} не обнаружен в БД.')

        QApplication.processEvents()
        self.professor.session().commit()
        self.session.expire_all()
        self.on_finish(f'Успешно загружены данные')
