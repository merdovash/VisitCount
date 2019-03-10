import sys
from typing import TypeVar

from PyQt5.QtCore import Qt, pyqtSignal, QModelIndex, QSize
from PyQt5.QtGui import QStandardItemModel
from PyQt5.QtWidgets import QComboBox, QApplication, QListView

from DataBase2 import Professor, Student

T = TypeVar('T')


class CheckableComboBox(QComboBox):
    currentChanged = pyqtSignal('PyQt_PyObject')

    def __init__(self, parent=None, with_all=False):
        super(CheckableComboBox, self).__init__(parent)
        self.setView(QListView(self))
        self.view().pressed.connect(self.handleItemPressed)
        self.setModel(QStandardItemModel(self))
        self.with_all = with_all
        self.items = []
        if self.with_all:
            self.addItem('All')

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
        super(CheckableComboBox, self).addItem(str(item))
        item = self.model().item(self.count() - 1, 0)
        item.setFlags(Qt.ItemIsUserCheckable | Qt.ItemIsEnabled)
        item.setCheckState(Qt.Unchecked)
        item.setSizeHint(QSize(self.width(), 25))

    def setItems(self, items):
        for item in items:
            self.addItem(item)

    def clear(self):
        super().clear()
        self.setModel(QStandardItemModel(self))
        self.items = []
        if self.with_all:
            self.addItem('All')

    # def addItem(self, *__args):
    #     model: QStandardItemModel = self.model()
    #     model.appendRow()


if __name__ == '__main__':
    app = QApplication(sys.argv)

    widget = CheckableComboBox()
    for st in Student.of(Professor.get(id=1)):
        widget.addItem(st)

    widget.show()
    widget.checked.connect(lambda x: print(widget.current()))

    sys.exit(app.exec_())
