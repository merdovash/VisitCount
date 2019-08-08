import logging

from DataBase2 import Visitation


def debug(user):
    """
    Исправляет все отрицаительные идентификаторы обратно на положительные
    :param user:
    :return:
    """
    count = 0
    for visit in Visitation.of(user):
        if visit.id < 0:
            count += 1
            visit.id *= -1
            user.session().commit()
    logging.getLogger("synch").info(f"debug wrong id count={count}")
