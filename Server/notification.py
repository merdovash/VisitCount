"""
notification
"""
import datetime
import smtplib


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

    def send_msg(self, student_id: int or str, skips: [SkipLesson]):
        """

        :param skips: list of SkipLesson
        :param student_id: student id
        :return: None
        """

        parent = self.db_worker.get_parent(student_id)

        if parent is not None:
            student = self.db_worker.get_students(student_id=student_id)[0]
            text = "From: Администрация СПбГУТ \n" \
                   "Subject: Пропуски занятий \n" \
                   "To: {} \n".format(parent["name"])
            text += "Уважаемый (-ая) {0}, \n".format(parent["name"])
            text += "Сообщаем вам, что по состоянию на {1} " \
                    "{0} имеет следующие пропуски в учебе: \n".format(student["name"],
                                                                      datetime.datetime.now())
            for l in skips:
                discipline = self.db_worker.get_disciplines(discipline_id=l.discipline_id)
                if len(discipline) > 0:
                    text += "{0} : {1} пропусков \n".format(discipline["name"], l.skipCount)
            text += "С уважением, Администрация СПбГУТ."

            self.server.sendmail(to_addrs=parent["email"], from_addr=self.config.email, msg=text.encode())

    def close(self):
        """
        close connection to email server
        """
        self.server.close()


def run(db_worker: 'DataBaseWorker', config) -> None:
    """

    Runs notification process of parents

    :param config:
    :param db_worker: database worker
    """
    print("notification started")
    password = input("Введите пароль: ")

    conn = MailConnection(db_worker, config.email, password, config)

    students_list = db_worker.get_students()
    for student in students_list:
        data_list = []

        disciplines_list = db_worker.get_disciplines(student_id=student["id"])
        for discipline in disciplines_list:
            total_lessons = db_worker.get_the_lessons_count(student["id"], discipline["id"])
            visited_lessons = db_worker.get_visited_lessons_count(student["id"], discipline["id"])

            max_loss = 3
            if total_lessons - visited_lessons >= int(max_loss):
                data_list.append((discipline["id"], total_lessons - visited_lessons))

        if not len(data_list) == 0:
            conn.send_msg(student["id"], data_list)
    conn.close()
