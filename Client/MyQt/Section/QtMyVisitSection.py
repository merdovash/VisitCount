from PyQt5.QtCore import Qt, QPoint
from PyQt5.QtWidgets import QTableWidget, QAbstractItemView

from Client.MyQt.QtMyWidgetItem import StudentHeaderItem, PercentHeaderItem, VisitItem, LessonDateItem
from Client.test import safe


class VisitSection(QTableWidget):
    @safe
    def __init__(self, *__args):
        super().__init__(*__args)

        self.horizontalHeader().setVisible(False)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
        self.setEditTriggers(QAbstractItemView.NoEditTriggers)

        self.setContextMenuPolicy(Qt.CustomContextMenu)
        self.customContextMenuRequested.connect(self.table_right_click)

        headers = self.verticalHeader()
        headers.setContextMenuPolicy(Qt.CustomContextMenu)
        headers.customContextMenuRequested.connect(self.vertical_header_click)

    def vertical_header_click(self, event: QPoint):
        print("Event on header")
        index = self.indexAt(event)
        row = index.row()
        item = self.verticalHeaderItem(row)
        if type(item) == StudentHeaderItem or type(item) == PercentHeaderItem:
            real_pos = event.__pos__() + self.pos()
            item.show_context_menu(real_pos)

    def table_right_click(self, event: QPoint):
        index = self.indexAt(event)
        row, col = index.row(), index.column()
        print(row, col)
        item = self.item(row, col)
        if type(item) == VisitItem:
            real_pos = event.__pos__() + self.pos()
            item.show_context_menu(real_pos)
        if type(item) == LessonDateItem:
            real_pos = event.__pos__() + self.pos()
            item.show_context_menu(real_pos)
