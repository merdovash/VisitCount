import collections
import datetime
from typing import List, Dict, TypeVar, Any, Callable

from PyQt5.QtCore import QRectF, pyqtSignal, pyqtSlot, QModelIndex, QSize, QSortFilterProxyModel
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPainter, QImage, QPen, QColor, QStandardItemModel
from PyQt5.QtWidgets import QComboBox, QWidget, QHBoxLayout, QLabel, QListView, QCompleter

from Client.MyQt.ColorScheme import Color
from Domain.functools.List import closest_lesson
from DataBase2 import Discipline, Group, Lesson, _DBPerson

compare = lambda x, y: collections.Counter(x) == collections.Counter(y)

T = TypeVar('T')


class MComboBox(QComboBox):
    image = QImage('Client/MyQt/Window/Main/icons/baseline_arrow_drop_down_black_18dp.png')

    default_pen = QPen(QColor(0, 0, 0))

    hovered_pen = QPen(Color.primary)
    hovered_pen.setWidth(3)

    current_changed = pyqtSignal('PyQt_PyObject', 'PyQt_PyObject')  # real signature (List[Lesson], T)

    label: str

    def filter_cond(self, item: T) -> Callable[[Lesson], bool]:
        """
        Фильтрует список занятий для соответсвия с item
        :param item:
        :return:
        """
        if hasattr(self.type, 'filter_cond'):
            return self.type.filter_cond(item)
        raise NotImplementedError()

    def extractor(self, item: Lesson) -> T:
        """
        Вычленяет значение элемента из занятия
        :param item:
        """
        if hasattr(self.type, 'extractor'):
            return self.type.extractor(item)
        raise NotImplementedError()

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
                [lesson for lesson in self.lessons if self.filter_cond(self.current())(lesson)],
                self.current()
            )

    @pyqtSlot('PyQt_PyObject', 'PyQt_PyObject', name='on_parent_change')
    def on_parent_change(self, lessons, parent_value):
        self.lessons = lessons
        if lessons is None or len(lessons) == 0:
            return

        data = sorted(list(set([self.extractor(item) for item in self.lessons])), key=self.sorter)
        self.set_items(data)
        self.setCurrent(self.extractor(closest_lesson(lessons)))

    def __init__(self, parent, type_: T):
        super().__init__()
        self.setParent(parent)
        self.type = type_
        self.lessons: List[Lesson] = list()

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
        try:
            return self.items[self.currentIndex()]
        except IndexError:
            return None

    def clear(self):
        print('clear', type(self))
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

    #def paintEvent(self, QPaintEvent):
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


class MCheckedComboBox(MComboBox):
    currentChanged = pyqtSignal('PyQt_PyObject')

    def __init__(self, parent, with_all, type_):
        super().__init__(parent, type_)
        self.setView(QListView(self))
        self.view().pressed.connect(self.handleItemPressed)
        self.setModel(QStandardItemModel(self))
        self.with_all = with_all
        self.items = []
        if self.with_all:
            self.addItem('All')

        self.setEditable(True)
        self.lineEdit().setReadOnly(True)
        self.editTextChanged.connect(lambda x: None)

        def set_current_text(current):
            if current is None or (isinstance(current, list) and len(current)==0):
                self.lineEdit().setText('None')
            elif isinstance(current, collections.Iterable):
                value = ', '.join(i.short_name() for i in current)
                self.lineEdit().setText(value)
            else:
                raise NotImplementedError()

        self.currentChanged.connect(set_current_text)

        self.setCurrentText('')

    def handleItemPressed(self, index: QModelIndex):
        def switch(item):
            if item.checkState() == Qt.Checked:
                item.setCheckState(Qt.Unchecked)
            else:
                item.setCheckState(Qt.Checked)

        print(index.row())
        if self.with_all and index.row() == 0:
            model: QStandardItemModel = self.model()
            all_item = self.model().itemFromIndex(index)
            switch(all_item)
            for row in range(len(self.items)):
                index = model.index(row + 1, index.column())
                item = self.model().itemFromIndex(index)
                if item is not None:
                    item.setCheckState(all_item.checkState())
        else:
            item = self.model().itemFromIndex(index)
            switch(item)

        self.currentChanged.emit(self.current())

    def setChecked(self, s_item):
        for index, item in enumerate(self.items):
            if item.id == s_item.id:
                index = self.model().index(index, 0)
                print('set', index)
                self.handleItemPressed(index)
                return
        raise IndexError(f'no item {s_item} in {self.items}')

    def current(self):
        checkedItems = []
        for index in range(1 if self.with_all else 0, self.count()):
            item = self.model().item(index)
            if item.checkState() == Qt.Checked:
                checkedItems.append(self.items[index])
        return checkedItems

    def addItem(self, item):
        self.items.append(item)
        super(MCheckedComboBox, self).addItem(str(item))
        item = self.model().item(self.count() - 1, 0)
        item.setFlags(Qt.ItemIsUserCheckable | Qt.ItemIsEnabled)
        item.setCheckState(Qt.Unchecked)
        item.setSizeHint(QSize(self.width(), 30))

    def set_items(self, items):
        for item in items:
            self.addItem(item)

    def clear(self):
        super().clear()
        self.setModel(QStandardItemModel(self))
        self.items = []
        if self.with_all:
            self.addItem('All')
        self.setCurrentText('None')

    @pyqtSlot('PyQt_PyObject', name='setCurrent')
    def setCurrent(self, item: T):
        self.setChecked(item)


class Selector(QWidget):
    def __init__(self, items: List[MComboBox], user: _DBPerson, flags=None):
        assert all(isinstance(item, MComboBox) for item in items)
        super().__init__(flags)

        main_layout = QHBoxLayout()
        for index, item in enumerate(items):
            main_layout.addWidget(QLabel(item.label), alignment=Qt.AlignRight | Qt.AlignVCenter, stretch=1)
            main_layout.addWidget(item, stretch=3)
            if index > 0:
                items[index - 1].current_changed.connect(item.on_parent_change)

        items[0].loads(user)

        self.setLayout(main_layout)
