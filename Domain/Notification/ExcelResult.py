import logging
import os
import smtplib
import asyncio
from abc import ABC, abstractmethod
from collections import namedtuple, defaultdict
from copy import copy
from datetime import datetime, timedelta
from email.mime.application import MIMEApplication
from email.mime.image import MIMEImage
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.utils import COMMASPACE, formatdate
from os.path import basename
from pathlib import Path
from typing import List, TypeVar, Dict, Any

import jinja2

import openpyxl

from DataBase2 import _DBEmailObject, Student, Professor, Group, _DBPerson
from Domain.Aggregation.Loss import student_loss
from Domain.Date import semester_start
from Domain.Notification import src
from Domain.functools.Format import inflect, Case
from Parser import server_args


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
    nothing_to_show = False

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
        def greeting():
            if isinstance(self.receiver, _DBPerson):
                return f"Уважаемый {self.receiver.full_name()},<br>Доводим до вашего сведения, что "
            else:
                return f"Сообщаем, что на {self.receiver.full_name(Case.loct).capitalize()} "

        def attach_image(msg, file_path: Path, id: str):
            with open(str(file_path), 'rb') as image:
                mime_image = MIMEImage(image.read(), file_path.suffix)
                mime_image.add_header('Content-ID', f'<{id}>')
                mime_image.add_header("Content-Disposition", "inline", filename=str(file_path))
                msg.attach(mime_image)

        def attach_document(msg, file_path: Path, id: str):
            with open(str(file_path), "rb") as file:
                part = MIMEApplication(
                    file.read(),
                    Name=basename(str(file_path))
                )
                part.add_header('Content-ID', f'<{id}>')
                part.add_header('Content-Disposition', 'attachment', filename=f"{basename(str(file_path))}")
                msg.attach(part)

        logger = logging.getLogger('notification')

        msg = MIMEMultipart()
        msg['From'] = "Администрация СПбГУТ"
        msg['To'] = COMMASPACE.join(self.receiver.email)
        msg['Date'] = formatdate(localtime=True)
        msg['Subject'] = "Автоматическая рассылка информация о пропусках"

        template_path = Path(f'Server/templates/{type(self.receiver).__name__}_email.html')
        print(template_path)
        with open(str(template_path), 'r') as email_sample:
            template = jinja2.Template(email_sample.read())

            if self.nothing_to_show:
                message = f"пропусков не было"
            else:
                message = f"следущие студенты пропустили занятия: (прикреплён файл)."

                attach_document(msg, Path(self.file_name), 'report')

            html = template.render(
                greeting=greeting(),
                start_interval=self.receiver.last_auto,
                end_interval=datetime.now(),
                message=message
            )
            mime_html = MIMEMultipart(_subtype='related')
            mime_html.attach(MIMEText(html, 'html'))
            attach_image(mime_html, Path('Server/resources/logo_sut_new.png'), 'logo')
            msg.attach(mime_html)

        try:
            smtp = smtplib.SMTP(server_args.smtp_server)
            smtp.ehlo()
            smtp.starttls()
            smtp.login(server_args.notification_email, server_args.notification_password)
            smtp.sendmail(server_args.notification_email, self.receiver.email, msg.as_string())
            logger.info(f'send result to {self.receiver.full_name()}')
            smtp.close()
        except Exception as e:
            logger.critical(e)
        else:
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
            cell.value = cell.value \
                .replace('%semester_start_date%', str(semester_start(self.receiver.last_auto))) \
                .replace('%now_date%', str(datetime.now()))

        def format_info_text(sheet):
            cell = sheet.cell(4, 1)
            cell.value = cell.value \
                .replace('%last_auto%', str(self.receiver.last_auto))

        def copy_cell_style(source, target):
            target.font = copy(source.font)
            target.fill = copy(source.fill)
            target.border = copy(source.border)
            target.alignment = copy(source.alignment)

        students = self.create()
        if len(students) == 0:
            self.nothing_to_show = True
            return

        data: Dict[Any, List[ExcelResult.info]] = defaultdict(list)
        for student in students:
            data[self.group_by(student)].append(student)

        sheet: openpyxl.workbook.workbook.Worksheet = self.form()
        format_date_text(sheet)
        format_info_text(sheet)
        current_row = self.head_row()
        sample_row = self.head_row() + 1
        for key, info in data.items():
            group_title = sheet.cell(current_row - 1, 2, key)
            copy_cell_style(sheet.cell(self.head_row() - 1, 2), group_title)

            for col_index in range(2, len(self.cols(info[0])) + 2):
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
        self.file_name = f'{self.receiver.short_name()}_{self.target_time}-{self.target_time+timedelta(0, self.receiver.interval_auto_hours*3600)}.xlsx'
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
