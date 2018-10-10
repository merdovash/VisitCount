"""
notification
"""
import datetime
import smtplib
from collections import namedtuple
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from typing import List

from DataBase.ServerDataBase import DataBaseWorker

SkipLesson = namedtuple('SkipLesson', 'discipline_id skip_count')


class MailConnection:
    """

    :param login: login to email
    :param password: password to email
    :return: connection to email server
    """

    def __init__(self, db_worker, login: str, password: str):
        self.config = db_worker.config
        self.db_worker = db_worker
        self.server = smtplib.SMTP('smtp.gmail.com:587')
        self.server.ehlo()
        self.server.starttls()
        self.server.login(login, password)

    def send_msg(self, student_id: int or str, skips: List[SkipLesson]):
        """

        :param skips: list of SkipLesson
        :param student_id: student id
        :return: None
        """

        parent = self.db_worker.get_parent(student_id)

        skips_count = len(skips)
        if parent is not None or skips_count == 0:
            student = self.db_worker.get_students(student_id=student_id)[0]

            text = """
            <html>
            <p>Уважаемый (-ая) {0}, <p>
            <p>Сообщаем вам, что по состоянию на {1} <br>
            {2} имеет следующие пропуски в учебе:<p>
            {3}
            <p> Данное письмо сформировано автоматически, пожалуйста не отвечайте на него <p>
            <p align=center> СПбГУТ, {4} <p>
            </html>
            """.format(
                parent["name"],
                datetime.datetime.now().isoformat(),
                student["first_name"],
                self._table(skips),
                datetime.datetime.now().year)

            message = MIMEMultipart("alternative", None, [MIMEText(text, 'html')])

            message["Subject"] = "Пропуски занятий"
            message['From'] = "Администрация СПбГУТ"
            message['To'] = parent["name"]

            self.server.sendmail(to_addrs=parent["email"],
                                 from_addr=self.config.email,
                                 msg=message.as_string())
        else:
            print("no parents, so sad")

    def _table(self, skips):
        html_table = """
        <table border='1px solid black'> 
            <tr> 
                <th> Дисциплина </th> 
                <th> Количество пропусков </th> 
            </tr>
        """

        for case in skips:
            discipline = self.db_worker.get_disciplines(discipline_id=case.discipline_id)
            discipline_count = len(discipline)
            if discipline_count > 0:
                discipline = discipline[0]
                html_table += self._table_row(discipline["name"], case.skip_count)

        html_table += "</table>"

        return html_table

    @staticmethod
    def _table_row(name, skip_count):
        return """
            <tr>
                <td align=center> {0} </td>
                <td align=center> {1} </td>
            </tr>
        """.format(name, skip_count)

    def close(self):
        """
        close connection to email server
        """
        self.server.close()


def run(database: DataBaseWorker) -> int:
    """

    Runs notification process of parents

    :param database: database worker
    :return: total length of table
    """
    print("notification started")
    if database.config.mail_password is None or "":
        database.config.mail_password = input("Введите пароль: ")

    conn = MailConnection(db_worker=database,
                          login=database.config.email,
                          password=database.config.mail_password)

    students_list = database.get_students()
    count = 0
    for student in students_list:
        data_list = []

        disciplines_list = database.get_disciplines(student_id=student["id"])
        # print(student["id"], disciplines_list)
        for discipline in disciplines_list:
            total_lessons = database.get_the_lessons_count(student["id"], discipline["id"])
            visited_lessons = database.get_visited_lessons_count(student["id"], discipline["id"])

            max_loss = 3
            if total_lessons - visited_lessons >= int(max_loss):
                data_list.append(SkipLesson(discipline["id"], total_lessons - visited_lessons))
                count += 1

        data_count = len(data_list)
        if data_count > 0:
            conn.send_msg(student["id"], data_list)
    conn.close()
    return count
