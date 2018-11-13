from collections import namedtuple
from datetime import datetime
from typing import List

import xlrd
from xlrd import Book
from xlrd.sheet import Sheet

from Client.IProgram import IProgram
from DataBase2 import Group, Student, Lesson
from Domain.Validation import ExcelValidation
from Domain.functools.Function import memoize
from Domain.functools.List import find

student = namedtuple('student', 'last_name first_name middle_name card_id visitations')
lesson = namedtuple('lesson', 'date col real_lesson')


class ExcelVisitationLoader:
    group_name_index = (0, 2)

    lesson_index_row = 1
    lesson_date_row = 3
    lesson_time_row = 4

    card_id_column = 1
    student_column = 2

    students_row = 5

    def __init__(self, program: IProgram, test=False):
        assert isinstance(program, IProgram), TypeError()
        self.program = program
        self.session = program.session

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

        return self.session.query(Group).filter(Group.name == group_name).first()

    def _get_lesson_header(self, sheet: Sheet, group: Group) -> List[lesson]:
        lessons = []
        real_lessons = sorted(Lesson.of(group), key=lambda x: x.date)
        print(list(map(lambda x: x.date, real_lessons)))

        year = datetime.now().year

        for col in range(self.student_column + 1, self.student_column + 1 + self._get_lessons_count(sheet)):
            date = sheet.cell(self.lesson_date_row, col).value
            if date is not None and date != '':
                index = int(sheet.cell(self.lesson_index_row, col).value)
                day, month = (int(v) for v in date.split('.'))
                hours, minutes = (int(v) for v in sheet.cell(self.lesson_time_row, col).value.split(':'))

                date = datetime(year=year, month=month, day=day, hour=hours, minute=minutes)

                real_lesson = find(lambda x: x.date == date, real_lessons)
                assert real_lesson is not None, f'no lesson for date {date}'
                lessons.append(lesson(date, col, real_lessons))

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
        else:
            raise NotImplementedError(student_cell)

    def _get_students(self, sheet: Sheet) -> List[student]:
        lesson_count = self._get_lessons_count(sheet)

        student_info = []

        for row in range(self.students_row, sheet.nrows):
            if sheet.cell(row, 0).value is not None and sheet.cell(row, 0).value != "":
                student_fio = self._extract_student_info(sheet, row)
                assert len(student_fio) == 3, f'row {row} is not valid, {student_fio}'
                last_name, first_name, middle_name = student_fio
                student_card_id = sheet.cell(row, self.card_id_column)
                visitation = []

                for lesson in range(lesson_count):
                    col = self.student_column + 1 + lesson

                    visit_cell = sheet.cell(row, col)
                    visitation.append(visit_cell.value == 1)

                student_info.append(student(last_name, first_name, middle_name, student_card_id, visitation))

        return student_info

    def read(self, file_path):
        assert isinstance(file_path, str), TypeError()
        wb = self._read_file(file_path)

        sheet = self._get_sheet(wb)

        db_group = self._get_group(sheet)

        db_students = Student.of(db_group)

        students = self._get_students(sheet)

        lessons = self._get_lesson_header(sheet, db_group)

        print(lessons, students)

    def test(self):
        self.read('/home/vlad/PycharmProjects/VisitCount/Domain/ExcelLoader/Группа_ИСТ_622.xls')


if __name__ == "__main__":
    e = ExcelVisitationLoader(IProgram())
    e.read('/home/vlad/PycharmProjects/VisitCount/Domain/ExcelLoader/Группа_ИСТ_621.xls')
