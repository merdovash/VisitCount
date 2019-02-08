from PyQt5.QtWidgets import QTableWidget, QTableWidgetItem

from DataBase2 import _DBObject


class QNewItemsTable(QTableWidget):
    def __init__(self, old_session, new_session, *__args):
        super().__init__(*__args)

        self.old_session = old_session
        self.new_session = new_session

        self.setColumnCount(2)

        self.setHorizontalHeaderItem(0, QTableWidgetItem('Имя'))
        self.setHorizontalHeaderItem(1, QTableWidgetItem('Статус'))

    def addItem(self, item: _DBObject):
        new = None
        current_row = self.rowCount()
        if item.session() == self.new_session:
            old_item = item.get(self.old_session, id=item.id)
            if old_item is not None:
                new = False
            else:
                new = True
        elif item.session() == self.old_session:
            new = False

        self.insertRow(current_row)

        self.setItem(current_row, 0, QTableWidgetItem(str(item)))
        self.setItem(current_row, 1, QTableWidgetItem('новый' if new else 'уже есть'))

        self.resizeColumnsToContents()
