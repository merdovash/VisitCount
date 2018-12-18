from sqlalchemy import inspect

from DataBase2 import Auth


def set_uid(auth: Auth, uid):
    session = inspect(auth).session

    auth.uid = uid

    session.commit()
