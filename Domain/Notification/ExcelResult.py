import logging
import os
import smtplib
import asyncio
import sys
import traceback
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
from typing import List, TypeVar, Dict, Any, Type, Callable

import jinja2

import openpyxl
from pandas import DataFrame

from DataBase2 import _DBEmailObject, Student, Professor, Group, _DBPerson, ContactInfo, Visitation, Lesson
from Domain.Aggregation.Loss import student_loss
from Domain.Data import names_of_groups
from Domain.Date import semester_start
from Domain.Notification import src
from Domain.functools.Format import inflect, Case
from Parser import server_args


class MessageMaker(ABC):
    file_name: str
    receiver: _DBEmailObject

    @abstractmethod
    def update(self, mime: MIMEMultipart)-> List[str]:
        pass

    @classmethod
    def auto(cls, receiver, target_time) -> Callable[[], None]:
        receiver = receiver
        contact: ContactInfo = receiver.contact
        target_time = target_time

        mime = MIMEMultipart()
        mime['From'] = "Администрация СПбГУТ"
        mime['To'] = receiver.contact.email
        mime['Date'] = str(target_time)
        mime['Subject'] = "Автоматическая рассылка информация о пропусках"

        logging.getLogger('notification').debug(f'{receiver}: {contact.views}')
        files = []
        for view in contact.views:
            name: str = view.script_path
            logging.getLogger('notification').debug(f'TRYING use {name} on {receiver}')
            try:
                maker_class: Type[MessageMaker] = eval(name)
                maker: MessageMaker = maker_class(receiver, target_time)
                attached_files = maker.update(mime)
                files.extend(attached_files)
            except Exception as e:
                print(e)
                logging.getLogger('notification').error(e)

        async def send():
            try:
                smtp = smtplib.SMTP(server_args.smtp_server)
                smtp.ehlo()
                smtp.starttls()
                smtp.login(server_args.notification_email, server_args.notification_password)
                smtp.sendmail(server_args.notification_email, receiver.contact.email, mime.as_string())
                logging.getLogger('notification').info(f'send result to {receiver.full_name()}')
                smtp.close()
            except Exception as e:
                logging.getLogger('notification').error(e)

            else:
                receiver.contact.last_auto = target_time
                receiver.session().commit()

            finally:
                for file_name in attached_files:
                    os.remove(file_name)

        return send


class ExcelResult(MessageMaker, ABC):
    info = TypeVar('info')
    file = None
    file_name: str
    nothing_to_show = False

    def __init__(self, receiver: _DBEmailObject, target_time: datetime):
        self.receiver = receiver
        self.target_time = target_time

    def update(self, mime: MIMEMultipart) -> List[str]:
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

        self.prepare_data()

        template_path = Path(f'Server/templates/{type(self.receiver).__name__}_email.html')
        with open(str(template_path), 'r') as email_sample:
            template = jinja2.Template(email_sample.read())

            if self.nothing_to_show:
                message = f"пропусков не было"
            else:
                message = f"следущие студенты пропустили занятия: (прикреплён файл)."

                attach_document(mime, Path(self.file_name), 'report')

            html = template.render(
                greeting=greeting(),
                start_interval=self.receiver.contact.last_auto,
                end_interval=datetime.now(),
                message=message
            )
            mime_html = MIMEMultipart(_subtype='related')
            mime_html.attach(MIMEText(html, 'html'))
            attach_image(mime_html, Path('Server/resources/logo_sut_new.png'), 'logo')
            mime.attach(mime_html)

            return [] if self.nothing_to_show else [self.file_name]

    def prepare_data(self) -> None:
        user = self.receiver
        df = DataFrame(
            {
                'student': student.full_name(),
                'group': group.short_name(),
                'date': lesson.date,
                'type': str(lesson.type),
                'completed': lesson.completed,
                'discipline': lesson.discipline.short_name(),
                'visited': len(set(Visitation.of(student)) & set(Visitation.of(lesson))),
                'semester': str(lesson.semester),
                'updated': max(lesson._updated, lesson._created)
            } for lesson in Lesson.of(user) for student in Student.of(lesson) for group in student.groups
            if not lesson._is_deleted
        )
        df_new: DataFrame = df.loc[(df['completed'] == True) & (df['visited'] == 0) & (df['updated'] > self.receiver.contact.last_auto)]
        df: DataFrame = df.loc[(df['student'].isin(df_new['student'].unique()))]
        df: DataFrame = df.groupby(['semester', 'group', 'student'])['visited'].count()
        df: DataFrame = df.reset_index()
        df.rename(columns={'semester': 'Семестр', 'group': "Группа", 'student': "Студент", 'visited': "Пропусков"},
                  inplace=True)

        if len(df) > 0:
            self.file_name = f'{self.receiver.short_name()}' \
                f'_{self.target_time}' \
                f'-{self.target_time + timedelta(0, self.receiver.contact.interval_auto_hours * 3600)}.xlsx'
            df.to_excel(self.file_name, columns=['Студент', "Пропусков"], index=None)

        else:
            self.nothing_to_show = True


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
            loss = student_loss(student, last_date=self.receiver.contact.last_auto)
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
