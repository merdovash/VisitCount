import collections
from typing import TypeVar, Callable

from PyQt5.QtCore import Qt
from PyQt5.QtCore import pyqtSignal, pyqtSlot, QModelIndex, QSize
from PyQt5.QtGui import QStandardItemModel, QMouseEvent
from PyQt5.QtWidgets import QListView, QLineEdit

from Client.MyQt.Widgets.ComboBox import QMComboBox
from Client.MyQt.Widgets.ComboBox.MComboBox import QMComboBox

compare = lambda x, y: collections.Counter(x) == collections.Counter(y)

T = TypeVar('T')


class _ClickableLineEdit(QLineEdit):
    def __init__(self, callback, *__args):
        super().__init__(*__args)
        self.callback = callback

    def mouseReleaseEvent(self, event: QMouseEvent):
        self.callback()


class QMCheckedComboBox(QMComboBox):
    currentChanged = pyqtSignal('PyQt_PyObject')

    def __init__(self, parent, with_all, type_):
        super().__init__(parent=parent, type_=type_)
        self.setView(QListView(self))
        self.view().pressed.connect(self.handleItemPressed)
        self.setModel(QStandardItemModel(self))
        self.with_all = with_all
        self.items = []
        if self.with_all:
            self.addItem('All', )

        self.setLineEdit(_ClickableLineEdit(lambda: self.showPopup()))
        self.setEditable(True)
        self.lineEdit().setReadOnly(True)
        print(self.lineEdit().mousePressEvent)

        self.editTextChanged.connect(lambda x: None)

        def set_current_text(current):
            if current is None or (isinstance(current, list) and len(current) == 0):
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

    def addItem(self, item, **kwargs):
        self.items.append(item)
        super(QMCheckedComboBox, self).addItem(str(item))
        item = self.model().item(self.count() - 1, 0)
        item.setFlags(Qt.ItemIsUserCheckable | Qt.ItemIsEnabled)
        item.setCheckState(Qt.Unchecked)
        item.setSizeHint(QSize(self.width(), 30))

    def set_items(self, items):
        for item in items:
            self.addItem(item, )

    def clear(self):
        super().clear()
        self.setModel(QStandardItemModel(self))
        self.items = []
        if self.with_all:
            self.addItem('All', )
        self.setCurrentText('None')

    @pyqtSlot('PyQt_PyObject', name='setCurrent')
    def setCurrent(self, item: T):
        self.setChecked(item)
