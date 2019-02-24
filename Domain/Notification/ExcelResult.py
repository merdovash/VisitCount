import smtplib
import asyncio
from abc import ABC, abstractmethod
from collections import namedtuple, defaultdict
from copy import copy
from datetime import datetime
from email.mime.application import MIMEApplication
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.utils import COMMASPACE, formatdate
from os.path import basename
from typing import List, TypeVar, Dict, Any

import openpyxl

from DataBase2 import _DBEmailObject, Student, Professor, Group
from Domain.Aggregation.Loss import student_loss
from Domain.Date import semester_start
from Domain.Notification import src
from Server import config


class MessageMaker(ABC):
    file_name: str
    receiver: _DBEmailObject

    @abstractmethod
    def send(self):
        pass


class ExcelResult(MessageMaker, ABC):
    info = TypeVar('info')
    file = None
    file_name: str

    def __init__(self, receiver: _DBEmailObject, target_time: datetime):
        self.receiver = receiver
        self.target_time = target_time

    def __del__(self):
        if self.file is not None:
            self.file.close()

    @abstractmethod
    def group_by(self, item):
        pass

    @abstractmethod
    def cols(self, item: info):
        pass

    @abstractmethod
    def form(self) -> openpyxl.Workbook:
        pass

    @abstractmethod
    def create(self) -> List[info]:
        pass

    def send(self):
        msg = MIMEMultipart()
        msg['From'] = "Администрация СПбГУТ"
        msg['To'] = COMMASPACE.join(self.receiver.email)
        msg['Date'] = formatdate(localtime=True)
        msg['Subject'] = "Автоматическая рассылка информация о пропусках"

        msg.attach(MIMEText("Автоматическая рассылка информация о пропусках."))

        with open(self.file_name, "rb") as file:
            part = MIMEApplication(
                file.read(),
                Name=basename(self.file_name)
            )

            part['Content-Disposition'] = f'attachment; filename="{basename(self.file_name)}"'
            msg.attach(part)

        smtp = smtplib.SMTP('smtp.gmail.com:587')
        smtp.ehlo()
        smtp.starttls()
        smtp.login(config.email, config.password)
        smtp.sendmail(config.email, self.receiver.email, msg.as_string())
        smtp.close()
        self.receiver.last_auto = self.target_time
        self.receiver.session().commit()

    @abstractmethod
    def head_row(self) -> int:
        return 6

    @abstractmethod
    def table_title_row(self) -> int:
        return 5

    def prepare(self):
        def format_date_text(sheet):
            cell = sheet.cell(3, 1)
            cell.value = cell.value\
                .replace('%semester_start_date%', str(semester_start(self.receiver.last_auto)))\
                .replace('%now_date%', str(datetime.now()))

        def format_info_text(sheet):
            cell = sheet.cell(4, 1)
            cell.value = cell.value\
                .replace('%last_auto%', str(self.receiver.last_auto))

        def copy_cell_style(source, target):
            target.font = copy(source.font)
            target.fill = copy(source.fill)
            target.border = copy(source.border)
            target.alignment = copy(source.alignment)

        students = self.create()

        data: Dict[Any, List[ExcelResult.info]] = defaultdict(list)
        for student in students:
            data[self.group_by(student)].append(student)

        sheet: openpyxl.workbook.workbook.Worksheet = self.form()
        format_date_text(sheet)
        format_info_text(sheet)
        current_row = self.head_row()
        sample_row = self.head_row()+1
        for key, info in data.items():
            group_title = sheet.cell(current_row-1, 2, key)
            copy_cell_style(sheet.cell(self.head_row()-1, 2), group_title)

            for col_index in range(2, len(self.cols(info[0]))+2):
                head_cell = sheet.cell(self.head_row(), col_index)

                new_head_cell = sheet.cell(current_row, col_index, head_cell.value)
                copy_cell_style(head_cell, new_head_cell)

            current_row += 1
            for row_index, i in enumerate(info, current_row):

                for col_index, value in enumerate(self.cols(i), 2):
                    cell = sheet.cell(row_index, col_index, value)
                    copy_cell_style(sheet.cell(sample_row, col_index), cell)

                current_row += 1

            current_row += 2
        self.file_name = f'{datetime.now()}.{self.receiver.email}.xlsx'
        self.file.save(self.file_name)


class OneListStudentsTotalLoss(ExcelResult):
    info = namedtuple('info', 'student loss')

    def cols(self, item: info):
        return item.student.full_name(), item.loss

    def group_by(self, item: info):
        cond = Group.of(item.student)
        if len(cond) == 1:
            return cond[0].full_name()
        return ','.join([f.short_name() for f in cond])

    def form(self):
        self.file = openpyxl.load_workbook(src.one_listed_students_total_form)
        self.sheet = self.file.active
        return self.sheet

    def create(self):
        students_info: List[OneListStudentsTotalLoss.info] = list()
        for student in Student.of(self.receiver, sort=lambda x: x.full_name()):
            loss = student_loss(student, last_date=self.receiver.last_auto)
            if loss is not None:
                students_info.append(self.info(student, loss))

        return students_info

    def head_row(self):
        return 7

    def table_title_row(self):
        return 6


if __name__ == '__main__':
    professor = Professor.get(id=1)
    professor.last_auto = datetime(2018, 10, 1)
    OneListStudentsTotalLoss(Professor.get(id=1))
