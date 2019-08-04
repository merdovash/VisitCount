from enum import Enum
from typing import Any, List, TypeVar

from PyQt5.QtCore import pyqtSignal, pyqtSlot, Qt
from PyQt5.QtGui import QImage, QPen, QColor
from PyQt5.QtWidgets import QComboBox

from Client.MyQt.ColorScheme import Color
from DataBase2 import Lesson, _Displayable, name
from Domain.Data import names_of_groups
from Domain.functools.Format import type_name

T = TypeVar('T')


class QMComboBox(QComboBox):
    image = QImage('Client/MyQt/Window/Main/icons/baseline_arrow_drop_down_black_18dp.png')

    default_pen = QPen(QColor(0, 0, 0))

    hovered_pen = QPen(Color.primary)
    hovered_pen.setWidth(3)

    current_changed = pyqtSignal('PyQt_PyObject', 'PyQt_PyObject')  # real signature (List[Lesson], T)

    label: str

    def formatter(self, item: T) -> str:
        if hasattr(self.type, 'formatter'):
            return self.type.formatter(item)
        raise NotImplementedError()

    def sorter(self, item: T) -> Any:
        if hasattr(self.type, 'sorter'):
            return self.type.sorter(item)
        raise NotImplementedError()

    @pyqtSlot(int, name='resignal')
    def resignal(self):
        if self.lessons is not None:
            self.current_changed.emit(
                Lesson.filter_lessons(self.current(), self.lessons),
                self.current()
            )

    @pyqtSlot('PyQt_PyObject', 'PyQt_PyObject', name='on_parent_change')
    def on_parent_change(self, lessons, parent_value):
        self.lessons = lessons
        if lessons is None or len(lessons) == 0:
            return

        data = sorted(self.type.of(lessons))
        self.set_items(data)
        self.setCurrent(self.type.of(Lesson.closest_to_date(lessons))[0])

    def __init__(self, type_: T = None, parent=None):
        super().__init__()
        self.setParent(parent)
        self.type = type_
        self.lessons: List[Lesson] = list()

        self.currentIndexChanged.connect(self.resignal)

        self.items: List[T] = []

        self.pending = None

        if issubclass(type_, Enum):
            self.addItems(type_)

    def setEngine(self, type_):
        self.type = type_

    def addItems(self, iterable: List[T], p_str=None) -> None:
        for i, value in enumerate(iterable):
            self.items.append(value)
            self.setItemData(i, f"{type_name(value)}: {name(value)}", Qt.ToolTipRole);
        else:
            super().addItems([name(i) for i in iterable])

    def current(self) -> _Displayable or None:
        try:
            return self.items[self.currentIndex()]
        except IndexError:
            return None

    def clear(self):
        super().clear()
        self.items = []

    @pyqtSlot('PyQt_PyObject', name='setCurrent')
    def setCurrent(self, item: T):
        if len(self.items) == 0:
            return

        if isinstance(item, list):
            item = item[0]

        index = self.items.index(item)
        if index >= 0:
            self.setCurrentIndex(index)
        else:
            raise ValueError(f"{item} not in items")

    # def paintEvent(self, QPaintEvent):
    #    p = QPainter(self)
    #
    #    rect = QRectF(0, 0, self.width(), self.height())
    #
    #    # p.fillRect(rect, Color.secondary)
    #
    #    p.setPen(self.default_pen if not self.underMouse() else self.hovered_pen)
    #    p.drawLine(0, rect.height() - 3, rect.width(), rect.height() - 3)
    #
    #    p.setPen(self.default_pen)
    #    p.drawText(rect, Qt.AlignCenter, self.currentText())
    #
    #    p.drawImage(rect.width() - self.image.width(), self.height() // 2 - self.image.height() // 2, self.image)

    def set_items(self, items):
        self.blockSignals(True)
        self.clear()
        self.addItems(items)
        self.blockSignals(False)
        self.resignal()

    def loads(self, user):
        self.lessons = Lesson.of(user)
        self.on_parent_change(self.lessons, None)

    def __repr__(self):
        return f"QMComboBox of {self.type}"


class QMMultipleComboBox(QMComboBox):
    def filter_lessons(self, lessons):
        return sorted([l for d, l in [(self.filter([l])[0], l) for l in lessons] if d == self.current()])

    def filter(self, lessons):
        data = sorted(list(set([frozenset(self.type.of(l)) for l in lessons])), key=names_of_groups)
        data = [list(d) for d in data]
        return data

    @pyqtSlot('PyQt_PyObject', 'PyQt_PyObject', name='on_parent_change')
    def on_parent_change(self, lessons, parent_value):
        self.lessons = lessons
        if lessons is None or len(lessons) == 0:
            return

        data = self.filter(lessons)
        self.set_items(data)
        self.setCurrent(self.filter([Lesson.closest_to_date(lessons)]))

    @pyqtSlot(int, name='resignal')
    def resignal(self):
        if self.lessons is not None:
            self.current_changed.emit(
                self.filter_lessons(self.lessons),
                self.current()
            )
