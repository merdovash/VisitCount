import logging
import os
import smtplib
from abc import ABC, abstractmethod
from collections import namedtuple
from datetime import datetime, timedelta
from email.mime.application import MIMEApplication
from email.mime.image import MIMEImage
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from os.path import basename
from pathlib import Path
from typing import List, TypeVar, Type, Callable, Dict, Tuple
from Domain.functools.Format import agree_to_number

import jinja2
from pandas import DataFrame

from DataBase2 import _DBEmailObject, Student, Professor, Group, _DBPerson, ContactInfo, Visitation, Lesson, Faculty, \
    Administration, Semester
from Domain.Aggregation.Loss import student_loss
from Domain.Notification.HTMLMaker import HTMLMaker
from Domain.functools.Format import Case
from Parser.server import server_args


class MessageMaker(ABC):
    file_name: str
    receiver: _DBEmailObject

    Subject: Dict[Type[_DBEmailObject], str] = {
        Faculty: "Пропуски занятий студентами",
        Administration: "Пропуски занятий студентами",
        Professor: "Пропуски ваших занятий"
    }

    @abstractmethod
    def update(self, mime: MIMEMultipart, html: HTMLMaker) -> List[str]:
        pass

    @classmethod
    def auto(cls, receiver, target_time) -> Callable[[], None] or None:
        receiver = receiver
        contact: ContactInfo = receiver.contact
        target_time = target_time

        mime = MIMEMultipart()
        mime['From'] = "Администрация СПбГУТ"
        mime['To'] = receiver.contact.email
        mime['Date'] = str(target_time)
        mime['Subject'] = cls.Subject[type(receiver)]

        html = HTMLMaker()

        logging.getLogger('notification').debug(f'{receiver}: {contact.views}')
        files = []
        have_data_to_show = False
        for view in contact.views:
            name: str = view.script_path
            logging.getLogger('notification').debug(f'TRYING use {name} on {receiver}')
            try:
                maker_class: Type[MessageMaker] = eval(name)
                print(maker_class)
                maker: MessageMaker = maker_class(receiver, target_time)
                add, attached_files = maker.update(mime, html)
                have_data_to_show |= add
                files.extend(attached_files)
            except Exception as e:
                print(e)
                logging.getLogger('notification').error(e)
        mime.attach(MIMEText(str(html), 'html'))

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

        if have_data_to_show:
            return send
        return


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


class Report(MessageMaker, ABC):
    info = TypeVar('info')
    file = None
    file_name: str = None
    nothing_to_show = False

    @abstractmethod
    def prepare_data(self):
        pass

    @abstractmethod
    def append_data(self, html: HTMLMaker):
        pass

    def __init__(self, receiver: _DBEmailObject, target_time: datetime):
        self.receiver = receiver
        print(self.receiver)
        self.target_time = target_time

    def update(self, mime: MIMEMultipart, html: HTMLMaker) -> Tuple[bool, List[str]]:
        self.prepare_data()

        if self.nothing_to_show:
            return False, []

        self.append_data(html)
        if self.file_name is not None:
            attach_document(mime, Path(self.file_name), id='report')

        return (True, []) if self.file_name is None else (True, [self.file_name])


class OneListStudentsTotalLoss(Report):
    def prepare_data(self):
        df = DataFrame(
            {
                'student': student.full_name(),
                'group': group.short_name(),
                'date': lesson.date,
                'type': lesson.type.short_name(),
                'completed': lesson.completed,
                'discipline': lesson.discipline.short_name(),
                'visited': len(set(Visitation.of(student)) & set(Visitation.of(lesson))),
                'semester': str(lesson.semester),
                'updated': max(lesson._updated, lesson._created)
            } for lesson in Lesson.of(self.receiver) for group in lesson.groups for student in group
            if not lesson._is_deleted
        )

        df_new: DataFrame = df.loc[
            (df['completed'] == True)
            & (df['visited'] == 0)
            & (df['updated'] > self.receiver.contact.last_auto)
            ]
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

        return df

    def append_data(self, html: HTMLMaker):
        if isinstance(self.receiver, Faculty):
            html.add_content(
                f'Оперативная информация о пропусках занятий студентами факультета {self.receiver.short_name()}  '
                f'на {self.target_time} размещена в прикрепленном файле')
        elif isinstance(self.receiver, Professor):
            html.add_content(f'Оперативная информация о пропусках занятий Преподавателя {self.receiver.short_name()}  '
                             f'на {self.target_time} размещена в прикрепленном файле')
        else:
            raise NotImplementedError(type(self.receiver))


class ProgramProcess(Report):
    def prepare_data(self):
        lessons = Lesson.of(self.receiver)
        now = datetime.now()
        df: DataFrame = DataFrame([
            {
                'completed': lesson.completed,
                'semester': lesson.semester.start_date,
                'date': lesson.date
            }
            for lesson in lessons])
        df: DataFrame = df.loc[(df['semester'] < now)]
        df: DataFrame = df.loc[df['semester'] == df['semester'].max()]
        self.rate = df.loc[df['completed'] == True].shape[0] / df.shape[0]
        self.leak = df.loc[(df['completed'] == False) & (df['date'] < now)].shape[0]

    def append_data(self, html: HTMLMaker):
        html.add_content(f'Прогресс выполнения программы {round(self.rate*100)}%.')
        if self.leak>0:
            html.add_content(f'Отставание от программы: {self.leak} {agree_to_number("занятие", self.leak)}')


if __name__ == '__main__':
    professor = Professor.get(id=1)
    professor.last_auto = datetime(2018, 10, 1)
    OneListStudentsTotalLoss(Professor.get(id=1))
