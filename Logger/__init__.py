import os
from datetime import datetime


class Logger:
    name = os.path.abspath(f'log_from_{datetime.now().isocalendar()}.log')

    @classmethod
    def write(cls, text):
        with open(Logger.name, 'a+') as file:
            file.write(f'{text}\n')
