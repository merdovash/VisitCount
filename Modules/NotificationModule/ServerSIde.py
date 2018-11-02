import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from flask import render_template

from DataBase2 import Auth, Administration, Parent
from DataBase2.Types import format_name
from Domain.Aggregation import GroupAggregation
from Domain.functools.List import flat
from Modules import Module
from Modules.NotificationModule import address
from Server import config, Response


class MessageMaker:
    rule = {
        Administration: 'admin_email.html',
        Parent: 'parent_email.html'
    }

    def __init__(self, user):
        self.user = user
        self.sender_name = format_name(user)

    def to(self, receiver):
        total_rate, group_table = GroupAggregation.by_professor(self.user, html=True)

        html_text = render_template(MessageMaker.rule[type(receiver)],
                                    receiver_name=format_name(receiver),
                                    sender_name=self.sender_name,
                                    visit_rate=total_rate,
                                    group_table=group_table)

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

        self.connection = self.connector()

    def connect(self, login, password):
        conn = smtplib.SMTP('smtp.gmail.com:587')
        conn.ehlo()
        conn.starttls()
        conn.login(login, password)

        return conn

    def post(self, data: dict, response: Response, auth: Auth, **kwargs):
        admins = Administration.of(auth.user)
        parents = Parent.of(auth.user)

        print(admins)

        message = MessageMaker(auth.user)

        for receiver in flat([admins, parents]):
            assert receiver.email is not None, f'receiver {receiver} email is None'
            print(receiver, receiver.email)
            try:
                self.connection.sendmail(
                    to_addrs=receiver.email,
                    from_addr=config.email,
                    msg=message.to(receiver)
                )
                print(f'send to {receiver.email}')
            except smtplib.SMTPRecipientsRefused:
                pass

        response.set_data({})
