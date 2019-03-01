from PyQt5.QtCore import Qt, QSortFilterProxyModel
from PyQt5.QtGui import QStandardItem, QStandardItemModel
from PyQt5.QtWidgets import QComboBox, QCompleter

from Domain.Data import student_info


class UserItem(QStandardItem):
    def __init__(self, user, *__args):
        self._item = user
        super().__init__(user.full_name(), *__args)

    def item(self):
        return self._item


class ExtendedCombo(QComboBox):
    def __init__(self, items=None, parent=None):
        super().__init__(parent)

        self.setFocusPolicy(Qt.StrongFocus)
        self.setEditable(True)
        self.completer = QCompleter(self)

        # always show all completions
        self.completer.setCompletionMode(QCompleter.UnfilteredPopupCompletion)
        self.pFilterModel = QSortFilterProxyModel(self)
        self.pFilterModel.setFilterCaseSensitivity(Qt.CaseInsensitive)

        self.completer.setPopup(self.view())

        self.setCompleter(self.completer)

        self.lineEdit().textEdited.connect(self.pFilterModel.setFilterFixedString)
        self.completer.activated.connect(self.setTextIfCompleterIsClicked)

    def setItems(self, items: list or set):
        self.items = list(items)

        model = QStandardItemModel()

        for i, student in enumerate(items):
            item = UserItem(student)
            model.setItem(i, 0, item)

        self.setModel(model)
        self.setModelColumn(0)

    def setModel(self, model):
        super(ExtendedCombo, self).setModel(model)
        self.pFilterModel.setSourceModel(model)
        self.completer.setModel(self.pFilterModel)

    def setModelColumn(self, column):
        self.completer.setCompletionColumn(column)
        self.pFilterModel.setFilterKeyColumn(column)
        super(ExtendedCombo, self).setModelColumn(column)

    def view(self):
        return self.completer.popup()

    def index(self):
        return self.currentIndex()

    def setTextIfCompleterIsClicked(self, text):
        if text:
            index = self.findText(text)
            self.setCurrentIndex(index)

    def currentItem(self):
        return self.items[self.currentIndex()]
