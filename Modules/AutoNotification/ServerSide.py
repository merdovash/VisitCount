import asyncio
import logging
from datetime import timedelta, datetime, time
from typing import List

from DataBase2 import _DBEmailObject, Session, ContactInfo
from Domain.Notification.Report import MessageMaker


def init(loop: asyncio.AbstractEventLoop = None):
    async def send(receiver: _DBEmailObject):
        contact: ContactInfo = receiver.contact
        sleep_until: datetime = contact.last_auto
        now = datetime.now()
        while sleep_until<now:
            sleep_until+=timedelta(0, 60 * 60 * contact.interval_auto_hours)
        # sleep_until: datetime = contact.last_auto + timedelta(0, 60 * 60 * contact.interval_auto_hours)
        send_message = MessageMaker.auto(receiver, sleep_until)
        if send_message is None:
            return
        sleep_time: int = (sleep_until - datetime.now()).total_seconds()
        logger.info(f'prepared for {receiver}, '
                    f'sleep {sleep_time}s., '
                    f'target time {sleep_until}, '
                    f'last auto {contact.last_auto}')
        if sleep_time > 0:
            await asyncio.sleep(sleep_time)
        await send_message()

    async def prepare(receiver: _DBEmailObject, next_loop: datetime):
        contact: ContactInfo = receiver.contact
        if contact.last_auto + timedelta(0, contact.interval_auto_hours * 3600) <= next_loop:
            await send(receiver)

    async def look():
        while 1:
            now = datetime.now()
            next_loop = datetime.now() + timedelta(0, ((55 if now.minute < 55 else 115) - now.minute - 1) * 60 + (
                    60 - now.second))
            session = Session()
            stats = dict()
            search_start = datetime.now()
            for class_ in _DBEmailObject.email_subclasses():
                if len(class_.__subclasses__()) == 0:
                    print(class_)
                    items: List[_DBEmailObject] = session.query(class_).all()
                    stats[class_.__name__] = dict(total=0, prepared=[])
                    stats[class_.__name__]['total'] = len(items)
                    for item in items:
                        print('\t', item)
                        contact: ContactInfo = item.contact
                        if contact is not None and contact.auto:
                            print('\t\t', 'prepare')
                            logger.info(f'receiver {item.full_name()} is active')
                            await prepare(item, next_loop)

            sleep = (next_loop - datetime.now()).total_seconds()
            logger.debug(stats)
            logger.info(f'elapsed time on seek {(datetime.now() - search_start).total_seconds()}s., sleep for {sleep}s.')
            if sleep > 0:
                await asyncio.sleep(sleep)
            else:
                await asyncio.sleep(0)

    logger = logging.getLogger('notification')

    if loop is None:
        loop = asyncio.new_event_loop()

    logger.info('auto notifications running')
    loop.run_until_complete(look())
