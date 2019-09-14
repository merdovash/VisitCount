import re
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import List

from DataBase2 import Student


class Loader:
    pass


class Reader(Loader):
    file = None
    suffix: List[str] = []

    @classmethod
    def check(cls, file):
        if not isinstance(file, Path):
            file = Path(file)

        return file.suffix in cls.suffix

    @classmethod
    def auto(cls, file, **kwargs):
        for class_ in cls.__subclasses__():
            if class_.check(file):
                return class_(file, **kwargs)


class WordReader(Reader):
    suffix = ['.docx']

    class Mode(Enum):
        LIST = 0
        LIST_IN_TABLE = 1



class ExcelReader(Reader):
    group_regex = re.compile(
        r'(?:(?:[Гг]рупп[аы])?\s?(?P<G>(?:[А-Яа-я]+-[0-9]+,?\s?)+))'
    )
    group_name_cell_index = (0,2)

    discipline_regex = re.compile(
        r'(?:(?:[Дд]исциплина\s?:?\s)?(?P<discipline>.+))'
    )

    day_regex = re.compile(
        r'(?:(?P<month>[0-9]+)[:.](?P<day>[0-9]+))'
    )

    DISCIPLINE_ROW = 0
    DISCIPLINE_START_COL = 3
    DISCIPLINE_END_COL = 21

    student_regex = re.compile(
        r'(?:(?P<last>[А-яа-яё]+) (?P<first>[А-яа-яё]+)(?: (?P<middle>[А-яа-яё]+))?)'
    )

    STUDENT_START_ROW = 5

    def get_student(self, row: int, students: List[Student]) -> Student or None:

        if not hasattr(self, '_students_cache') or self._students_cache is None:
            self._students_cache = {}

        if row not in self._students_cache.keys():
            student_fio = self.student_regex.findall(self.file.cell(row, 2).value)
            if student_fio:
                student_fio = student_fio[0]

                if len(student_fio) == 0:
                    self._students_cache[row] = None
                if len(student_fio) == 2:
                    self._students_cache[row] = [
                        s
                        for s in students
                        if s.last_name == student_fio[0] and s.first_name == student_fio[1]
                    ][0]
                if len(student_fio) == 3:
                    self._students_cache[row] = [
                        s
                        for s in students
                        if s.last_name == student_fio[0] and s.first_name == student_fio[1] and s.middle_name == student_fio[2]
                    ][0]

            else:
                self._students_cache[row] = None

        return self._students_cache[row]

    def get_date(self, col: int, year: int) -> datetime:
        try:
            day = self.day_regex.findall(self.file.cell(3, col).value)[0]
            time = self.day_regex.findall(self.file.cell(4, col).value)[0]
        except IndexError:
            return None

        date = datetime(year, int(day[1]), int(day[0]), int(time[0]),int(time[1]))
        return date

    def group_name(self):
        value = self.file.cell(*self.group_name_cell_index).value
        return self.group_regex.findall(value)

    def discipline_name(self):
        for col in range(self.DISCIPLINE_START_COL, self.DISCIPLINE_END_COL):
            r = self.discipline_regex.findall(self.file.cell(self.DISCIPLINE_ROW, col).value)
            if r:
                return r[0]
        raise ValueError('Название дисциплины не найдено (ожидается, что оно находится в первой строке между '
                         'столбцами D и X)')

    suffix = ['.xls', '.xlsx']


class NetworkLoader(Loader):
    _has_data = False

    def has_data(self):
        raise NotImplementedError()
