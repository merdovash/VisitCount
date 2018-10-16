from PyQt5.QtCore import QPoint
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPainter, QColor, QCursor
from PyQt5.QtWidgets import QHeaderView, QTableWidgetItem

from Client.MyQt.ColorScheme import Color
from Client.MyQt.Table.Items.StudentHeader.StudentHeaderItem import StudentHeaderItem


class NoItemException(Exception):
    pass


class StudentHeaderView(QHeaderView):
    no_card_color = Color.primary_light
    primary_color = Color.secondary

    def __init__(self, Qt_Orientation):
        super().__init__(Qt_Orientation)

        self.line_color = QColor(0, 0, 0)
        self.rect_color = QColor(255, 255, 255)

        self.row_height = 19

        self.hovered = -1

        self.installEventFilter(self)

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

    def some(self):
        # for row in range(6):
        #    if not self.parent().isRowHidden(row):
        #        headerHeight += self.row_height
        #    else:
        #        hidden_row_count += 1
        #
        # p.drawRect(0, 0 - offset, headerWidth - 1, headerHeight)
        # p.drawLine(0, 0 - offset, headerWidth - 1, headerHeight - offset)
        #
        # p.drawText(headerWidth / 3, headerHeight / 3 * 2 - offset, 'Студенты')
        # p.drawText(headerWidth / 3 * 2, headerHeight / 3 - offset, 'Дата')
        #:
        pass

    def eventFilter(self, object, event):
        if event.type() in [10, 183, 12]:
            try:
                _, row = self.find_item(QCursor.pos())

                self.set_hovered(row)

                return True
            except:
                self.set_hovered(-1)
                return False

        elif event.type() == 11:
            self.set_hovered(-1)

            return True

        return False

    def find_item(self, pos: QPoint) -> (QTableWidgetItem, int):
        y = pos.y()
        current = self.mapToGlobal(self.pos()).y() - self.pos().y()

        for row in range(self.parent().rowCount()):
            height = self.parent().rowHeight(row)
            if current <= y < current + height:
                return self.parent().horizontalHeaderItem(row), row

            current += height

        raise NoItemException('position out of range')

    def set_hovered(self, index):
        if self.hovered != index:
            self.hovered = index if index is not None else -1
            self.model().headerDataChanged.emit(Qt.Vertical, 0, self.parent().rowCount())
