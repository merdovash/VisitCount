"""
notification
"""
import datetime
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from typing import List


class SkipLesson:
    def __init__(self, discipline_id, skipCount):
        self.discipline_id = discipline_id
        self.skipCount = skipCount


class MailConnection:
    """

    :param login: login to email
    :param password: password to email
    :return: connection to email server
    """

    def __init__(self, db_worker, login: str, password: str, config):
        self.config = config
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

        parents = self.db_worker.get_parents(student_id)

        for parent in parents:
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

            self.server.sendmail(to_addrs=parent["email"], from_addr=self.config.email, msg=message.as_string())
        else:
            print("no parents, so sad")

    def _table(self, skips):
        tb = "<table border='1px solid black'> <tr> <th> Дисциплина </th> <th> Количество пропусков </th> </tr>"

        for l in skips:
            discipline = self.db_worker.get_disciplines(discipline_id=l.discipline_id)
            if len(discipline) > 0:
                discipline = discipline[0]
                tb += self._table_row(discipline["name"], l.skipCount)

        tb += "</table>"

        return tb

    def _table_row(self, name, skipCount):
        return """
            <tr>
                <td align=center> {0} </td>
                <td align=center> {1} </td>
            </tr>
        """.format(name, skipCount)

    def close(self):
        """
        close connection to email server
        """
        self.server.close()


def run(db_worker: 'DataBaseWorker', config) -> int:
    """

    Runs notification process of parents

    :param config:
    :param db_worker: database worker
    :return: total length of table
    """
    print("notification started")
    if config.mail_password is None or "":
        config.mail_password = input("Введите пароль: ")

    conn = MailConnection(db_worker, config.email, config.mail_password, config)

    students_list = db_worker.get_students()
    count = 0
    for student in students_list:
        data_list = []

        disciplines_list = db_worker.get_disciplines(student_id=student["id"])
        print(student["id"], disciplines_list)
        for discipline in disciplines_list:
            total_lessons = db_worker.get_the_lessons_count(student["id"], discipline["id"])
            visited_lessons = db_worker.get_visited_lessons_count(student["id"], discipline["id"])

            max_loss = 3
            if total_lessons - visited_lessons >= int(max_loss):
                data_list.append(SkipLesson(discipline["id"], total_lessons - visited_lessons))
                count += 1

        if not len(data_list) == 0:
            conn.send_msg(student["id"], data_list)
    conn.close()
    return count
