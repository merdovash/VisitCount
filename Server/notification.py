"""
notification
"""
import datetime
import smtplib
import config
import sql_handler

import telebot


telegram_url = "https://api.telegram.org/bot/"+config.telegram_url+"/"

class Bot():
	def __init__(self, token):
		self.bot = telebot.TeleBot("https://api.telegram.org/bot/"+token+"/")
		




def create_connection(login: str, password: str):
    """

    :param login: login to email
    :param password: password to email
    :return: connection to email server
    """
    server = smtplib.SMTP('smtp.gmail.com:587')
    server.ehlo()
    server.starttls()
    server.login(login, password)

    def send_msg(db_worker, student_id: int or str, disciplines: list):
        """

        :param db_worker:  data base worker
        :param student_id: student id
        :param disciplines: data of loss
        :return: None
        """
        try:
            parent = db_worker.get_parent(student_id)
        except Exception:
            return
        student = db_worker.get_students(student_id=student_id)[0]
        text = "From: Администрация СПбГУТ \n" \
               "Subject: Пропуски занятий \n" \
               "To: {} \n".format(parent["name"])
        text += "Уважаемый (-ая) {0}, \n".format(parent["name"])
        text += "Сообщаем вам, что по состоянию на {1} " \
                "{0} имеет следующие пропуски в учебе: \n".format(student["name"],
                                                                  datetime.datetime.now())
        for discipline in disciplines:
            text += "{0} : {1} пропусков \n".format(db_worker.get_disciplines(discipline[0]), discipline[1])
        text += "С уважением, Администрация СПбГУТ."

        server.sendmail(to_addrs=parent["email"], from_addr=config.email, msg=text.encode())

    def close():
        """
        close connection to email server
        """
        server.close()

    return send_msg, close


def run(db_worker: sql_handler.DataBaseWorker) -> None:
    """

    Runs notification process of parents

    :param db_worker: database worker
    """
    print("notification started")
    password = input("Введите пароль: ")

    send_notification, close = create_connection(config.email, password)

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
            send_notification(student["id"], data_list)
    close()
