from PyQt5.QtCore import QPoint
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPainter, QColor, QMouseEvent
from PyQt5.QtWidgets import QHeaderView, QTableWidgetItem

from Client.MyQt.ColorScheme import Color
from Client.MyQt.Table.Items import AbstractContextItem
from Client.MyQt.Table.Items.StudentHeader.StudentHeaderItem import StudentHeaderItem


class NoItemException(Exception):
    pass


class StudentHeaderView(QHeaderView):
    no_card_color = Color.primary_light
    primary_color = Color.secondary

    def __init__(self):
        super().__init__(Qt.Vertical)

        self.line_color = QColor(0, 0, 0)
        self.rect_color = QColor(255, 255, 255)

        self.row_height = 19

        self.hovered = -1

        self.installEventFilter(self)
        self.setContextMenuPolicy(Qt.CustomContextMenu)
        self.customContextMenuRequested.connect(self.vertical_header_click)
        self.setSectionResizeMode(QHeaderView.Fixed)
        self.setMouseTracking(True)

    def vertical_header_click(self, event: QPoint):
        """
        Slot
        Shows context menu on vertical header item under mouse pointer
        :param event: point on screen
        """
        print(type(event))
        index = self.parent().indexAt(event)
        row = index.row()
        item = self.parent().verticalHeaderItem(row)
        if isinstance(item, AbstractContextItem):
            real_pos = self.mapToGlobal(event.__pos__())
            item.show_context_menu(real_pos)

    def paintEvent(self, QPaintEvent):
        p = QPainter(self.viewport())

        offset = self.parent().verticalOffset()

        row_height = self.row_height
        headerWidth = self.size().width()
        headerHeight = 0
        hidden_row_count = 0

        start_pixel = headerHeight
        for row in range(self.parent().model().rowCount()):
            try:
                text, bg_color, height = self.data(row)

                p.fillRect(0, start_pixel - offset,
                           headerWidth, height, bg_color)

                text = text
                p.drawText(8, 15 + start_pixel - offset, str(text))

                p.drawLine(0, start_pixel + height - 1 - offset,
                           headerWidth, start_pixel + height - 1 - offset)

                start_pixel += height
            except NoItemException:
                print('no item', row)

    def data(self, row):
        item = self.parent().verticalHeaderItem(row)

        if item is None:
            raise NoItemException()

        if isinstance(item, StudentHeaderItem):
            if item.have_card():
                if row == self.hovered:
                    rect_color = Color.primary_light_accent
                else:
                    rect_color = self.no_card_color
            else:
                if row == self.hovered:
                    rect_color = Color.secondary_accent
                else:
                    rect_color = self.primary_color
        else:
            if row == self.hovered:
                rect_color = Color.secondary_accent
            else:
                rect_color = self.primary_color

        return item.text(), rect_color, self.parent().rowHeight(row)

    def mouseMoveEvent(self, event: QMouseEvent):
        try:
            _, row = self.find_item(event.pos())

            self.set_hovered(row, True)

        except NoItemException:
            self.set_hovered(-1, True)

    def find_item(self, pos: QPoint) -> (QTableWidgetItem, int):
        def find_row(target_y):
            current_y = - self.parent().verticalOffset()

            for row in range(self.parent().rowCount()):
                height = self.parent().rowHeight(row)
                if current_y <= target_y <= current_y + height:
                    return row

                current_y += height
            else:
                return -1

        row = find_row(pos.y())

        return self.parent().verticalHeaderItem(row), row

    def set_hovered(self, index, pure=False):
        if self.hovered != index:
            self.hovered = index if index is not None else -1
            self.model().headerDataChanged.emit(Qt.Vertical, 0, self.parent().rowCount())

        if pure:
            self.parent().set_hover(index, -1)
