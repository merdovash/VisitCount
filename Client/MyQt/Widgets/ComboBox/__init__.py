import collections
import datetime
from typing import List, Dict, TypeVar, Any, Callable

from PyQt5.QtCore import QRectF, pyqtSignal, pyqtSlot
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPainter, QImage, QPen, QColor
from PyQt5.QtWidgets import QComboBox

from Client.MyQt.ColorScheme import Color
from Domain.functools.List import closest_lesson
from DataBase2 import Discipline, Group, Lesson

compare = lambda x, y: collections.Counter(x) == collections.Counter(y)

T = TypeVar('T')

class MComboBox(QComboBox):
    image = QImage('Client/MyQt/Window/Main/icons/baseline_arrow_drop_down_black_18dp.png')

    default_pen = QPen(QColor(0, 0, 0))

    hovered_pen = QPen(Color.primary)
    hovered_pen.setWidth(3)

    current_changed = pyqtSignal('PyQt_PyObject', 'PyQt_PyObject')

    def filter_cond(self, item)->Callable[[Any], bool]:
        raise NotImplementedError()

    def extractor(self, item)-> Any:
        raise NotImplementedError()

    def formatter(self, item)-> str:
        raise NotImplementedError()

    def sorter(self, item) -> Any:
        raise NotImplementedError()

    @pyqtSlot(int, name='resignal')
    def resignal(self):
        if self.lessons is not None:
            self.current_changed.emit(list(filter(self.filter_cond(self.current()), self.lessons)), self.current())

    @pyqtSlot('PyQt_PyObject', 'PyQt_PyObject', name='on_parent_change')
    def on_parent_change(self, lessons, parent_value):
        self.lessons = lessons

        data = sorted(list(set([self.extractor(item) for item in self.lessons])), key=self.sorter)
        self.set_items(data)
        self.setCurrent(self.extractor(closest_lesson(lessons)))

    def __init__(self, parent, type_: T):
        super().__init__()
        self.setParent(parent)
        self.type = type_
        self.lessons: List[Lesson] = None

        self.currentIndexChanged.connect(self.resignal)

        self.items: List[T] = []

        self.pending = None

    def addItems(self, iterable: List[T], p_str=None) -> None:
        print(iterable)
        for i, value in enumerate(iterable):
            # print(i, value)
            self.items.append(value)
        else:
            super().addItems([self.formatter(i) for i in iterable])

    def current(self) -> T:
        return self.items[self.currentIndex()]

    def clear(self):
        print('clear', type(self))
        super().clear()
        self.items = []

    @pyqtSlot('PyQt_PyObject', name='setCurrent')
    def setCurrent(self, item: T):
        if isinstance(item, list):
            item = item[0]

        index = self.items.index(item)
        if index >= 0:
            self.setCurrentIndex(index)
        else:
            raise ValueError(f"{item} not in items")

    def paintEvent(self, QPaintEvent):
        p = QPainter(self)

        rect = QRectF(0, 0, self.width(), self.height())

        # p.fillRect(rect, Color.secondary)

        p.setPen(self.default_pen if not self.underMouse() else self.hovered_pen)
        p.drawLine(0, rect.height() - 3, rect.width(), rect.height() - 3)

        p.setPen(self.default_pen)
        p.drawText(rect, Qt.AlignCenter, self.currentText())

        p.drawImage(rect.width() - self.image.width(), self.height() // 2 - self.image.height() // 2, self.image)

    def set_items(self, items):
        self.blockSignals(True)
        self.clear()
        self.addItems(items)
        self.blockSignals(False)
        self.resignal()
