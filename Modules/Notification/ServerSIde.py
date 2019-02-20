import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from flask import render_template
from premailer import transform

from DataBase2 import Auth, Administration, Parent, Lesson
from Domain.Aggregation import GroupAggregation, DisciplineAggregator, WeekDaysAggregation
from Domain.Structures.DictWrapper.Network.Notification import Reciever, NotificationResponse
from Domain.functools.Format import format_name
from Modules import Module
from Modules.Notification import address
from Server import config, Response


class MessageMaker:
    rule = {
        Administration: 'admin_email.html',
        Parent: 'parent_email.html'
    }

    def __init__(self, user):
        self.user = user
        self.sender_name = format_name(user)
        self.to_sender_name = format_name(self.user, case={'gent'})

        lessons = sorted(Lesson.of(user), key=lambda x: x.date)

        self.lessons_count = len(lessons)
        self.completed_count = len(list(filter(lambda x: x.completed == 1, lessons)))
        self.first_lesson_date = lessons[0].date
        self.last_lesson_date = lessons[-1].date

        self.total_rate, self.group_table = GroupAggregation.by_professor(self.user, html=True)

        self.discipline_table = DisciplineAggregator.by_professor(self.user).to_html()

        self.week_day_table = WeekDaysAggregation.by_professor(self.user).to_html()

    def to(self, receiver):
        html_text = transform(
            render_template(
                MessageMaker.rule[type(receiver)],
                total_count=self.lessons_count,
                completed_count=self.completed_count,
                first_lesson_date=self.first_lesson_date,
                last_lesson_date=self.last_lesson_date,
                receiver_name=format_name(receiver),
                sender_name=self.sender_name,
                to_sender_name=self.to_sender_name,
                visit_rate=self.total_rate,
                group_table=self.group_table,
                discipline_table=self.discipline_table,
                week_day_table=self.week_day_table
            )
        )

        message = MIMEMultipart("alternative", None, [MIMEText(html_text, 'html')])
        message["Subject"] = "Пропуски занятий"
        message['From'] = "Администрация СПбГУТ"
        message['To'] = format_name(receiver)

        return message.as_string()


class NotificationModule(Module):
    def __init__(self, app, request):
        assert config.email is not None and config.password is not None, 'config is not complete (email, password)'
        super().__init__(app, request, address)
        self.connector = lambda: self.connect(config.email, config.password)

        self.connection = None

    def connect(self, login, password):
        conn = smtplib.SMTP('smtp.gmail.com:587')
        conn.ehlo()
        conn.starttls()
        conn.login(login, password)

        return conn

    def post(self, data: dict, response: Response, auth: Auth, **kwargs):
        if self.connection is None:
            self.connection = self.connector()
        admins = Administration.active_of(auth.user)
        parents = Parent.of(auth.user)

        message = MessageMaker(auth.user)

        failed_users = []
        success_count = 0

        for receiver in sum([admins, parents], []):
            assert receiver is not None, f'receiver is None'
            assert receiver.email is not None, f'receiver {receiver} email is None'
            try:
                self.connection.sendmail(
                    to_addrs=receiver.email,
                    from_addr=config.email,
                    msg=message.to(receiver)
                )
                success_count += 1
            except smtplib.SMTPRecipientsRefused:
                failed_users.append(
                    Reciever(id=receiver.id, class_name=receiver)
                )
            except smtplib.SMTPSenderRefused:
                self.connection = self.connector()

                self.connection.sendmail(
                    to_addrs=receiver.email,
                    from_addr=config.email,
                    msg=message.to(receiver)
                )
                success_count += 1

        response.set_data(
            NotificationResponse(
                success_count=success_count,
                wrong_emails=failed_users
            )
        )