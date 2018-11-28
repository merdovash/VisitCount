import collections
import datetime
from typing import List, Dict, TypeVar

from PyQt5.QtCore import QRectF
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPainter, QImage, QPen, QColor
from PyQt5.QtWidgets import QComboBox

from Client.MyQt.ColorScheme import Color
from DataBase2 import Discipline, Group, Lesson

compare = lambda x, y: collections.Counter(x) == collections.Counter(y)

T = TypeVar('T')

class MComboBox(QComboBox):
    image = QImage('Client/MyQt/Window/Main/icons/baseline_arrow_drop_down_black_18dp.png')

    default_pen = QPen(QColor(0, 0, 0))

    hovered_pen = QPen(Color.primary)
    hovered_pen.setWidth(3)

    def __init__(self, type_: T):
        super().__init__()

        self.type = type_

        self.rule = {
            Discipline: lambda x: x.name,
            Group: lambda x: ', '.join(list(map(lambda y: y.name, x))),
            Lesson: lambda x: x.date.strftime('%d.%m.%Y %H:%M')
        }[self.type]

        self.items: Dict[int, type_] = {}

        self.pending = None

    def addItems(self, iterable: List[T], p_str=None) -> None:
        for i, value in enumerate(iterable):
            # print(i, value)
            self.items[i] = value
        else:
            super().addItems([self.rule(i) for i in iterable])

    def current(self) -> T:
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

    def setCurrent(self, item: T):
        # print(self.items)
        for i, value in enumerate(self.items):
            if self.type == Group:
                if compare(self.items[i], item):
                    super().setCurrentIndex(i)
                    return
            else:
                if self.items[i] == item:
                    super().setCurrentIndex(i)
                    return
        if len(self.items) == 0:
            self.pending = item
        else:
            raise IndexError('no such', item, 'in', self.items)

    def paintEvent(self, QPaintEvent):
        p = QPainter(self)

        rect = QRectF(0, 0, self.width(), self.height())

        # p.fillRect(rect, Color.secondary)

        p.setPen(self.default_pen if not self.underMouse() else self.hovered_pen)
        p.drawLine(0, rect.height() - 3, rect.width(), rect.height() - 3)

        p.setPen(self.default_pen)
        p.drawText(rect, Qt.AlignCenter, self.currentText())

        p.drawImage(rect.width() - self.image.width(), self.height() // 2 - self.image.height() // 2, self.image)
