import datetime
from typing import List, Dict

from PyQt5.QtWidgets import QComboBox

from Client.test import safe
from DataBase2 import Discipline, Group, Lesson


class QMyComboBox(QComboBox):
    def __init__(self, type_, image_type=None):
        super().__init__()

        self.type = type_

        self.rule = {
            Discipline: lambda x: x.name,
            Group: lambda x: ', '.join(list(map(lambda y: y.name, x))),
            Lesson: lambda x: x.date.strftime('%d.%m.%Y %H:%M')
        }[self.type]

        self.items: Dict[int, type_] = {}

    def addItems(self, iterable: List, p_str=None) -> None:
        for i, value in enumerate(iterable):
            # print(i, value)
            self.items[i] = value
        pass
        super().addItems([self.rule(i) for i in iterable])

    def current(self):
        return self.items[self.currentIndex()]

    def get_data(self):
        return [self.items[key] for key in self.items]

    def _format_name(self, value):
        if self.image_name == 'date':
            val = datetime.datetime.strptime(value, '%Y-%m-%d %H:%M:%f')
            return val.strftime('%d.%m.%Y %H:%M')
        else:
            return value

    def clear(self):
        super().clear()
        self.items = {}

    @safe
    def setCurrent(self, item):
        assert isinstance(item, self.type if self.type is not Group else list), f'{item} is not a {self.type}'
        # print(self.items)
        for i, value in enumerate(self.items):
            if self.items[i] == item:
                super().setCurrentIndex(i)
                return
        raise IndexError("no such item {} in {}".format(item, self.items))
