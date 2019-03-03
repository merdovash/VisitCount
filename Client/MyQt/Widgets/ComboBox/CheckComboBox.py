import sys
from typing import Generic, TypeVar

from PyQt5.QtCore import Qt, QAbstractListModel
from PyQt5.QtGui import QStandardItemModel, QStandardItem
from PyQt5.QtWidgets import QComboBox, QApplication

from Client.MyQt.Widgets.ComboBox import MComboBox
from DataBase2 import Professor, Student

T = TypeVar('T')


class CheckComboBoxModel(QAbstractListModel):
    def flags(self, index):
        return Qt.ItemIsUserCheckable | Qt.ItemIsSelectable | Qt.ItemIsEnabled


class CheckComboBox(QComboBox):
    def __init__(self, parent=None, proxy=None):
        super().__init__(parent)

        self._model = CheckComboBoxModel()
        self.proxy = proxy

        self.setModel(self._model)

    def addItems(self, Iterable, p_str=None):
        for item in Iterable:
            q_item = QStandardItem()
            if self.proxy is None:
                q_item.setText(str(item))
            else:
                q_item.setText(self.proxy.formatter(item))
            q_item.setCheckable(True)
            q_item.setSelectable(True)
            q_item.setCheckState(Qt.Unchecked)
            self.model().setItem(self.model().rowCount(), 0, q_item)

    def handleItemPressed(self, index):
        item = self.model().itemFromIndex(index)
        if item.checkState() == Qt.Checked:
            item.setCheckState(Qt.Unchecked)
        else:
            item.setCheckState(Qt.Checked)


class CheckableComboBox(QComboBox):
    # once there is a checkState set, it is rendered
    # here we assume default Unchecked
    def addItem(self, item):
        super(CheckableComboBox, self).addItem(str(item))
        item = self.model().item(self.count()-1,0)
        item.setFlags(Qt.ItemIsUserCheckable | Qt.ItemIsEnabled)
        item.setCheckState(Qt.Unchecked)

    def itemChecked(self, index):
        item = self.model().item(index,0)
        return item.checkState() == Qt.Checked


if __name__ == '__main__':
    app = QApplication(sys.argv)

    widget = CheckableComboBox()
    for st in Student.of(Professor.get(id=1)):
        widget.addItem(st)

    widget.show()

    sys.exit(app.exec_())
