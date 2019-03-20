import xlrd

from DataBase2 import Lesson, is_None, Student, Visitation
from Domain.Data import lessons_of
from Domain.Loader import ExcelReader, Loader


class VisitationLoader(Loader):
    def get_visitations(self):
        raise NotImplementedError()


class VisitationExcelLoader(ExcelReader, VisitationLoader):
    def __init__(self, file_name, group, discipline, session):
        file = xlrd.open_workbook(file_name)
        self.file = file.sheet_by_index(0)

        assert set([g.name for g in group]) == set(self.group_name())
        assert discipline.name.lower() == self.discipline_name().lower()

        lessons = lessons_of(group, discipline)
        year = sorted(lessons, key=lambda x: x.date)[0].date.year

        student_of_group = Student.of(group)

        for col in range(3, self.file.ncols):
            if self.file.cell(1, col).value in ['', None]:
                print((1, col), 'is None')
                break

            date = self.get_date(col, year)
            lesson = list(filter(lambda x: x.date == date, lessons))
            if len(lesson) == 0:
                continue
            lesson = lesson[0]

            for row in range(self.file.nrows):
                student = self.get_student(row, student_of_group)
                if student is None:
                    break
                print('new_visit', student, lesson)
                Visitation.get_or_create(session, student_id=student.id, lesson_id=lesson.id)

    def get_visitations(self):
        pass
