import threading
import time
from collections import defaultdict, namedtuple
from datetime import datetime, timedelta
from itertools import groupby
from pprint import pprint
from typing import List, Dict, Set, FrozenSet
import asyncio

from DataBase2 import Session, _DBEmailObject, Lesson, Discipline, Student, Visitation, Group
from Domain.Notification.ExcelResult import OneListStudentsTotalLoss

student_loss = namedtuple('student_loss', 'student loss total_lessons')


def init():
    async def send(reciever: _DBEmailObject, registerer: List):
        sleep_until = reciever.last_auto + timedelta(0, 60 * 60 * reciever.interval_auto_hours)
        mm = OneListStudentsTotalLoss(reciever, sleep_until)
        mm.prepare()
        sleep_time = (sleep_until - datetime.now()).total_seconds()
        registerer.append(dict(user=reciever, time_dalta=sleep_time))
        if sleep_time > 0:
            await time.sleep(sleep_time)
        mm.send()

    async def prepare(reciever: _DBEmailObject, next_loop: datetime, registerer: List):
        if reciever.last_auto + timedelta(0, reciever.interval_auto_hours*3600) <= next_loop:
            print(f'prepare {reciever}')
            await send(reciever, registerer)

    async def look():
        while True:
            now = datetime.now()
            next_loop = datetime.now()+timedelta(0, ((55 if now.minute < 55 else 115) - now.minute - 1) * 60 + (60 - now.second))
            session = Session()
            stats = dict()
            search_start = datetime.now()
            for class_ in _DBEmailObject.email_subclasses():
                if len(class_.__subclasses__()) == 0:
                    items: List[_DBEmailObject] = session.query(class_).all()
                    stats[class_.__name__] = dict(total=0, prepared=[])
                    stats[class_.__name__]['total'] = len(items)
                    for item in items:
                        if item.auto:
                            await prepare(item, next_loop, stats[class_.__name__]['prepared'])

            sleep = (next_loop-datetime.now()).total_seconds()
            pprint(stats)
            print(f'elapsed time on seek {(datetime.now() - search_start).total_seconds()}s.\n'
                  f'sleep for {sleep}s.')
            time.sleep(sleep)

    loop = asyncio.get_event_loop()
    loop.run_until_complete(look())


if __name__ == '__main__':
    init()
