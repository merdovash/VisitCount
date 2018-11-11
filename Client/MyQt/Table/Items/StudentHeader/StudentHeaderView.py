from PyQt5.QtCore import QPoint, QRectF
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPainter, QColor, QMouseEvent, QPen
from PyQt5.QtWidgets import QHeaderView, QTableWidgetItem

from Client.MyQt.ColorScheme import Color
from Client.MyQt.Table import PercentHeaderItem
from Client.MyQt.Table.Items import AbstractContextItem
from Client.MyQt.Table.Items.StudentHeader.StudentHeaderItem import StudentHeaderItem


class NoItemException(Exception):
    pass


class StudentHeaderView(QHeaderView):
    no_card_color = Color.primary_light
    primary_color = Color.secondary

    border_pen = QPen(Color.secondary_dark)
    border_pen.setWidthF(0.5)

    textPen = QPen(Color.text_color)

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

        row_count = self.parent().model().rowCount()

        start_pixel = headerHeight
        for row in range(row_count):
            try:
                item = self.parent().verticalHeaderItem(row)

                if isinstance(item, StudentHeaderItem):
                    self.draw_item(p, item, row, headerWidth, [0, start_pixel])
                elif isinstance(item, PercentHeaderItem):
                    y_pos = self.height() - self.parent().rowHeight(row) * (
                                row_count - row - 1) + self.parent().verticalOffset() - self.parent().horizontalScrollBar().height() - 14
                    self.draw_item(p, item, row, headerWidth, [0, y_pos])
                else:
                    raise NotImplementedError(type(item))

                start_pixel += self.parent().rowHeight(row)
            except NoItemException:
                print('no item', row)

    def draw_item(self, p: QPainter, item, row, width, started_point):
        height = self.parent().rowHeight(row)

        rect = QRectF(started_point[0] - self.parent().horizontalOffset(),
                      started_point[1] - self.parent().verticalOffset(),
                      width, height)

        p.fillRect(rect, self.get_color(item, row))

        p.setPen(self.textPen)
        p.drawText(rect, Qt.AlignCenter, item.text())

        p.setPen(self.border_pen)
        p.drawRect(rect)

    def get_color(self, item, row):
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
        return rect_color

    def mouseMoveEvent(self, event: QMouseEvent):
        try:
            _, row = self.find_item(event.pos())

            self.set_hovered(row, True)

        except NoItemException:
            self.set_hovered(-1, True)

    def find_item(self, pos: QPoint) -> (QTableWidgetItem, int):
        def find_row(target_y):
            last_row_height = self.parent().rowHeight(self.parent().rowCount() - 1)
            if target_y > self.height() - last_row_height:
                return self.parent().rowCount() - 1
            elif target_y > self.height() - last_row_height * 2:
                return self.parent().rowCount() - 2
            else:
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
