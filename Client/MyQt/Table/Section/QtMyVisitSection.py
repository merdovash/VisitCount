from PyQt5.QtCore import Qt, QPoint
from PyQt5.QtWidgets import QTableWidget, QAbstractItemView

from Client.MyQt.Table.Items import AbstractContextItem


class VisitSection(QTableWidget):

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
        """
        Slot
        Shows context menu on vertical header item under mouse pointer
        :param event: point on screen
        """
        index = self.indexAt(event)
        row = index.row()
        item = self.verticalHeaderItem(row)
        if isinstance(item, AbstractContextItem):
            real_pos = self.mapToGlobal(event.__pos__())
            item.show_context_menu(real_pos)

    def table_right_click(self, event: QPoint):
        """
        Slot
        Shows context menu of item under mouse pointer if item is AbstractContextItem
        :param event:
        """
        index = self.indexAt(event)
        row, col = index.row(), index.column()
        item = self.item(row, col)

        if isinstance(item, AbstractContextItem):
            real_pos = self.mapToGlobal(event.__pos__())
            item.show_context_menu(real_pos)
