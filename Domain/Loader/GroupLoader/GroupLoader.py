import re
from collections import namedtuple
from typing import List, Type

from docx import Document

from DataBase2 import Student, Group
from Domain.Loader import WordReader, Reader
from Domain.Loader.GroupLoader import GroupLoader


class GroupWordLoader(WordReader, GroupLoader):
    def get_students_list(self):
        return self.students

    def get_group_name(self) -> str:
        return self.group_name

    group_regex = re.compile(
        r'(?:(?:[Гг]руппа)\s)?([А-Яа-я]+\s?-\s?[0-9]+)(?:\s(?:[Гг]руппа))?'
    )

    full_name_regex = re.compile(
        r'^\s*((?:(?:[А-Яа-я])+(?:-[А-Яа-я]+)?\s){1,2}(?:(?:[А-Яа-я])+(?:-[А-Яа-я]+)?))\s*(?:[,.;])?\s*(?:[,.;])?$'
    )

    start_table = namedtuple('start_table', 'table row col')

    def __init__(self, file):
        self.doc: Document = Document(str(file))

        self.mode: GroupWordLoader.Mode = None
        self.start_paragraph: int = None

        self._get_group_name()
        self._get_students_list()

    def _get_group_name(self):
        for row_index, paragraph in enumerate(self.doc.paragraphs):
            groups = self.group_regex.findall(paragraph.text)

            if len(groups) > 0 and groups[0] is not None and groups[0] != '':
                self.mode = WordReader.Mode.LIST
                self.start_paragraph = row_index + 1

                self.group_name = groups[0].replace(' ', '')

        for table in self.doc.tables:
            for row_index, row in enumerate(table.rows):
                for col_index, cell in enumerate(table.row_cells(row_index)):
                    groups = self.group_regex.findall(cell.text)

                    if len(groups) > 0 and groups[0] is not None and groups[0] != '':
                        self.mode = WordReader.Mode.LIST_IN_TABLE
                        self.start_table = GroupWordLoader.start_table(table, row_index + 1, col_index)

                        self.group_name = groups[0].replace(' ', '')

    def _get_students_list(self):
        def get_student(text):
            full_name = self.full_name_regex.findall(text)
            if full_name is not None and len(full_name) > 0 and full_name[0] != '':
                splited = full_name[0].split(' ')
                return Student.get_or_create(
                    last_name=splited[0],
                    first_name=splited[1],
                    middle_name=splited[2] if len(splited) >= 3 else ''
                )

        students = []
        if self.mode == WordReader.Mode.LIST:
            for paragraph in self.doc.paragraphs[self.start_paragraph:]:
                student_name = get_student(paragraph.text)
                if student_name is not None:
                    students.append(student_name)

            if len(students) == 0:
                for table in self.doc.tables:
                    for cell in table._cells:
                        student_name = get_student(cell.text)
                        if student_name is not None:
                            students.append(student_name)

        elif self.mode == WordReader.Mode.LIST_IN_TABLE:
            start_row = self.start_table.row
            main_col = self.start_table.col
            table = self.start_table.table
            for row_index, row in enumerate(table.rows[start_row:], start_row):
                cells = table.row_cells(row_index)
                if len(cells) >= main_col:
                    cell = cells[main_col]
                    student_name = get_student(cell.text)
                    if student_name is not None:
                        students.append(student_name)

        self.students = sorted(students, key=lambda x: str(x))


class GroupAutoLoader(GroupLoader):
    def get_group(self)->Group:
        return self.worker.get_group()

    def get_students_list(self) -> List[Student]:
        return self.worker.get_students_list()

    workers: List[Type[Reader]] = [GroupWordLoader]

    def __init__(self, file_path):
        for class_ in self.workers:
            if class_.check(file_path):
                self.worker: GroupLoader = class_(file_path)
                break
        else:
            raise TypeError(f'unsupported file {file_path}')


if __name__ == '__main__':
    gr = GroupWordLoader('test3.docx')
    gr.get_group_name()
    print(gr.get_students_list())
