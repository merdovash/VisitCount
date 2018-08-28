import sched
import time

from DataBase.config2 import DataBaseConfig
from DataBase.sql_handler import DataBaseWorker
from Server.notification import run


class NotificationModule:
    def __init__(self, db):
        self.s = sched.scheduler(time.time, time.sleep)

        self.s.enter(10, 1, print, argument=('hello'))
        self.s.enter(60 * 60 * 24, 1, run, kwargs={'database': db})

        self.s.run()

if __name__=="__main__":
    NotificationModule(DataBaseWorker(DataBaseConfig()))
