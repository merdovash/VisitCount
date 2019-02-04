import re
from collections import namedtuple

from docx import Document

from Domain.Loader import WordReader
from Domain.Loader.GroupLoader import GroupLoader


class GroupWordReader(WordReader, GroupLoader):
    group_regex = re.compile(
        r'(?:(?:[Гг]руппа)\s)?([А-Яа-я]+\s?-\s?[0-9]+)(?:\s(?:[Гг]руппа))?'
    )

    full_name_regex = re.compile(
        r'^\s*((?:(?:[А-Яа-я])+(?:-[А-Яа-я]+)?\s){1,2}(?:(?:[А-Яа-я])+(?:-[А-Яа-я]+)?))\s*(?:[,.;])?\s*(?:[,.;])?$'
    )

    start_table = namedtuple('start_table', 'table row col')

    def __init__(self, file):
        self.doc: Document = Document(str(file))

        self.mode: GroupWordReader.Mode = None
        self.start_paragraph: int = None

    def get_group_name(self):
        for row_index, paragraph in enumerate(self.doc.paragraphs):
            groups = self.group_regex.findall(paragraph.text)

            if len(groups) > 0 and groups[0] is not None and groups[0] != '':
                self.mode = WordReader.Mode.LIST
                self.start_paragraph = row_index + 1

                return groups[0].replace(' ', '')

        for table in self.doc.tables:
            for row_index, row in enumerate(table.rows):
                for col_index, cell in enumerate(table.row_cells(row_index)):
                    groups = self.group_regex.findall(cell.text)

                    if len(groups) > 0 and groups[0] is not None and groups[0] != '':
                        self.mode = WordReader.Mode.LIST_IN_TABLE
                        self.start_table = GroupWordReader.start_table(table, row_index + 1, col_index)

                        return groups[0].replace(' ', '')

    def get_students_list(self):
        def get_student_name(text):
            full_name = self.full_name_regex.findall(text)
            if full_name is not None and len(full_name) > 0 and full_name[0] != '':
                splited = full_name[0].split(' ')
                return GroupLoader.student(*splited)

        students = []
        if self.mode == WordReader.Mode.LIST:
            for paragraph in self.doc.paragraphs[self.start_paragraph:]:
                student_name = get_student_name(paragraph.text)
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
                    student_name = get_student_name(cell.text)
                    if student_name is not None:
                        students.append(student_name)

        return students


class GroupAutoLoader:
    def __init__(self, file_path):
        self.file_path = file_path


if __name__ == '__main__':
    gr = GroupWordReader('test3.docx')
    gr.get_group_name()
    print(gr.get_students_list())
