from collections import namedtuple
from datetime import datetime
from typing import List, Dict

import xlrd
from PyQt5.QtCore import QUrl
from xlrd import Book
from xlrd.sheet import Sheet

from Client.IProgram import IProgram
from DataBase2 import Group, Student, Lesson
from Domain import Action
from Domain.Exception.Action import UnnecessaryActionException
from Domain.Validation import ExcelValidation
from Domain.functools.Decorator import memoize
from Domain.functools.List import find

student = namedtuple('student', 'real_student visitations new_card_id')
lesson = namedtuple('lesson', 'date col real_lesson')
visitation = namedtuple('visitation', 'col status')


def try_except(handler):
    def decorator(func):
        def input(*args, **kwargs):
            try:
                func(*args, **kwargs)
            except:
                handler()
                raise

        return input

    return decorator


class ExcelVisitationLoader:
    group_name_index = (0, 2)

    lesson_index_row = 1
    lesson_date_row = 3
    lesson_time_row = 4

    card_id_column = 1
    student_column = 2

    students_row = 5

    def __init__(self, program: IProgram, window=None, test=False):
        assert isinstance(program, IProgram), TypeError()
        self.program = program
        self.session = program.session

        if window is not None:
            self.read = try_except(window.exit.emit)(self.read)

        if test:
            self.test()

    def _read_file(self, path) -> Book:
        """
        Открывает excel файл и возвращает его

        :param path: путь к файлу
        :return: excel книга
        """
        return xlrd.open_workbook(path)

    def _get_sheet(self, wb) -> Sheet:
        """
        Возвращает страницу с посещениями

        :param wb:
        :return: страница excel книги
        """
        return wb.sheet_by_index(0)

    def _get_group(self, sheet) -> Group:
        raw_group_name = sheet.cell(*self.group_name_index)
        group_name = ExcelValidation.group_name(raw_group_name.value)

        return self.session.query(Group).filter(Group.name.in_(group_name)).all()

    def _get_lesson_header(self, sheet: Sheet, group: Group) -> Dict[int, lesson]:
        lessons = {}
        real_lessons = sorted(Lesson.of(group), key=lambda x: x.date)

        year = datetime.now().year

        for col in range(self.student_column + 1, self.student_column + 1 + self._get_lessons_count(sheet)):
            date = sheet.cell(self.lesson_date_row, col).value
            if date is not None and date != '':
                index = int(sheet.cell(self.lesson_index_row, col).value)
                day, month = (int(v) for v in date.split('.'))
                hours, minutes = (int(v) for v in sheet.cell(self.lesson_time_row, col).value.split(':'))

                date = datetime(year=year, month=month, day=day, hour=hours, minute=minutes)

                real_lesson = find(lambda x: x.date == date, real_lessons)
                if real_lesson is not None:
                    lessons[col] = lesson(date, col, real_lesson)
                else:
                    self.program.window.ok_message.emit(f'Для даты {month}.{day} {hours}:{minutes} не найдено '
                                                        f'совпадений в БД. Записи о посещениях будут пропущены. \n'
                                                        f'Для записи пропущенных данных измените дату занятия в '
                                                        f'программе или в документе и повторите попытку (дупликаты '
                                                        f'посещений будут проигнорированы при повторном запуске).')
                    lessons[col] = None

        return lessons

    @memoize
    def _get_lessons_count(self, sheet: Sheet) -> int:
        count = 0
        for col in range(self.student_column + 1, sheet.ncols):
            cell = sheet.cell(self.lesson_index_row, col)
            if not isinstance(cell.value, (float, int)) or cell.value is None:
                return count
            else:
                count += 1

    def _extract_student_info(self, sheet, row):
        student_cell = sheet.cell(row, self.student_column).value
        student_cell = student_cell.split(' ')
        if len(student_cell) == 3:
            return student_cell[0], student_cell[1], student_cell[2]
        elif len(student_cell) == 2:
            return student_cell[0], student_cell[1], ''
        elif len(student_cell) == 4 and (student_cell[3] == "*" or student_cell[3] == "**"):
            return student_cell[0], student_cell[1], student_cell[2]
        else:
            raise NotImplementedError(student_cell)

    def _get_students(self, sheet: Sheet, group: Group) -> List[student]:
        lesson_count = self._get_lessons_count(sheet)

        real_students = Student.of(group)

        student_info = []

        for row in range(self.students_row, sheet.nrows):
            if sheet.cell(row, 0).value is not None and sheet.cell(row, 0).value != "":
                student_fio = self._extract_student_info(sheet, row)
                assert len(student_fio) == 3, f'row {row} is not valid, {student_fio}'
                last_name, first_name, middle_name = student_fio
                student_card_id = int(sheet.cell(row, self.card_id_column).value)
                visitations = []

                for lesson in range(lesson_count):
                    col = self.student_column + 1 + lesson

                    visit_cell = sheet.cell(row, col)
                    visitations.append(visitation(col, visit_cell.value == 1))

                real_student = find(
                    lambda x: x.last_name == last_name and x.first_name == first_name and x.middle_name == middle_name,
                    real_students)
                assert real_student is not None, f'no such student for {student_fio}'

                student_info.append(student(real_student, visitations, student_card_id))

        return student_info

    def read(self, file_path, progress_bar=None):
        """

        :param progress_bar: индикатор для отображения прогресса чтения
        :param file_path: принимает строку адреса или QUrl объект
        """
        if isinstance(file_path, str):
            pass
        if isinstance(file_path, QUrl):
            file_path = file_path.toLocalFile()
        else:
            raise NotImplementedError(type(file_path))

        progress_updated = self.progress_updater_factory(progress_bar)

        wb = self._read_file(file_path)

        sheet = self._get_sheet(wb)

        db_group = self._get_group(sheet)

        students = self._get_students(sheet, db_group)

        lessons = self._get_lesson_header(sheet, db_group)

        total = len(students) * len(lessons)
        read = 0

        for col in lessons.keys():
            l = lessons[col]
            if l is not None:
                try:
                    Action.start_lesson(lesson=l.real_lesson, professor=self.program.professor)
                except UnnecessaryActionException:
                    pass

        for st in students:
            try:
                Action.change_student_card_id(
                    student=st.real_student,
                    new_card_id=st.new_card_id,
                    professor_id=self.program.professor.id
                )
            except UnnecessaryActionException:
                pass

            for visit in st.visitations:
                if lessons[visit.col] is not None \
                        and lessons[visit.col].real_lesson.completed \
                        and visit.status:
                    try:
                        Action.new_visitation(student=st.real_student,
                                              lesson=lessons[visit.col].real_lesson,
                                              professor_id=self.program.professor.id)
                    except UnnecessaryActionException:
                        pass
                read += 1
                progress_updated(int(read / total * 100))

    def progress_updater_factory(self, progress_bar):
        def nothing(value):
            pass

        def main(value):
            progress_bar.setValue(value)

        if progress_bar is None:
            return nothing
        elif hasattr(progress_bar, 'setValue'):
            return main
        else:
            raise NotImplementedError()

    def test(self):
        self.read('/home/vlad/PycharmProjects/VisitCount/Domain/ExcelLoader/Группа_ИСТ_622.xls')


if __name__ == "__main__":
    e = ExcelVisitationLoader(IProgram())
    e.read('/home/vlad/PycharmProjects/VisitCount/Domain/ExcelLoader/Группа_ИСТ_621.xls')
