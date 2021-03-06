import asyncio
import logging
from datetime import timedelta, datetime
from typing import List

from DataBase2 import _DBEmailObject, Session, ContactInfo
from Domain.Notification.Report import MessageMaker


def init(loop: asyncio.AbstractEventLoop = None):
    async def send(receiver: _DBEmailObject):
        contact: ContactInfo = receiver.contact
        sleep_until: datetime = contact.last_auto
        now = datetime.now()
        while sleep_until < now:
            sleep_until += timedelta(hours=contact.interval_auto_hours)

        send_message = MessageMaker.auto(receiver, sleep_until)
        if send_message is None:
            return

        sleep_time: float = (sleep_until - datetime.now()).total_seconds()
        logger.info(f'prepared for {receiver}, '
                    f'sleep {sleep_time}s., '
                    f'target time {sleep_until}, '
                    f'last auto {contact.last_auto}')

        if sleep_time > 0:
            await asyncio.sleep(sleep_time)
        await send_message()

    async def look():
        def is_time_to_prepare(contact):
            if contact.last_auto and contact.interval_auto_hours:
                is_time = contact.last_auto + timedelta(0, contact.interval_auto_hours * 3600) <= next_loop
                has_lessons = receiver.has_lessons_since(contact.last_auto)
                return contact.auto and is_time and has_lessons

            return contact.auto

        while 1:
            tasks = []

            now = datetime.now()
            next_loop = datetime.now() \
                + timedelta(0, ((55 if now.minute < 55 else 115) - now.minute - 1) * 60 + (60 - now.second))

            session = Session()
            stats = dict()
            search_start = datetime.now()
            for class_ in _DBEmailObject.email_subclasses():
                if len(class_.__subclasses__()) == 0:
                    receivers: List[_DBEmailObject] = session.query(class_).all()
                    stats[class_.__name__] = dict(total=0, prepared=[])
                    stats[class_.__name__]['total'] = len(receivers)
                    for receiver in receivers:
                        contact: ContactInfo = receiver.contact
                        if not contact:
                            continue
                        if is_time_to_prepare(contact):
                            logger.info(f'receiver {receiver.full_name()} is active')
                            tasks.append(loop.create_task(send(receiver)))

            for task in tasks:
                await task

            sleep = (next_loop - datetime.now()).total_seconds()
            logger.debug(stats)
            logger.info(
                f'elapsed time on seek {(datetime.now() - search_start).total_seconds()}s., sleep for {sleep}s.')
            if sleep > 0:
                await asyncio.sleep(sleep)
            else:
                await asyncio.sleep(0)

    logger = logging.getLogger('notification')

    if loop is None:
        loop = asyncio.new_event_loop()

    logger.info('auto notifications running')
    loop.run_until_complete(look())
