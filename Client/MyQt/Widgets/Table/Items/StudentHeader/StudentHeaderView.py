from typing import List

from PyQt5.QtCore import QPoint, QRectF, pyqtSignal, QSizeF
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPainter, QColor, QMouseEvent, QPen
from PyQt5.QtWidgets import QHeaderView, QTableWidgetItem

from Client.MyQt.ColorScheme import Color
from Client.MyQt.Widgets.Table import PercentHeaderItem, StudentHeaderItem
from Client.MyQt.Widgets.Table.Items import AbstractContextItem
from Client.MyQt.Widgets.Table.Section import Markup
from DataBase2 import Student
from Domain.Data import names_of_groups


class NoItemException(Exception):
    pass


class StudentHeaderView(QHeaderView):
    no_card_color = Color.primary_light
    primary_color = Color.secondary

    border_pen = QPen(Color.secondary_dark)
    border_pen.setWidthF(0.5)

    textPen = QPen(Color.text_color)

    hover_changed = pyqtSignal(int)

    students: List[Student] = None

    def __init__(self, parent):
        super().__init__(Qt.Vertical, parent=parent)

        self.line_color = QColor(0, 0, 0)
        self.rect_color = QColor(255, 255, 255)

        self.row_height = 19

        self.installEventFilter(self)
        self.setContextMenuPolicy(Qt.CustomContextMenu)
        self.customContextMenuRequested.connect(self.vertical_header_click)
        self.setSectionResizeMode(QHeaderView.Fixed)

        self.row_clicked = -1

    def set_students(self, students):
        self.students = students
        self.show_with_group_name = any([s.groups != students[0].groups for s in students])

    def setOffset(self, p_int):
        super().setOffset(p_int)
        self.model().dataChanged.emit(self.model().index(0, 0),
                                      self.model().index(1, len(self.students) - 1))

        self.viewport().update()

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

        headerWidth = self.size().width()
        headerHeight = 0

        start_pixel = headerHeight
        for row, student in enumerate(self.students+[None, None]):
            try:
                item: StudentHeaderItem or PercentHeaderItem = self.parent().verticalHeaderItem(row)

                if isinstance(item, StudentHeaderItem):
                    self.draw_item(p, item, student, row, headerWidth, [0, start_pixel])
                elif isinstance(item, PercentHeaderItem):
                    rect = QRectF(
                        QPoint(
                            0,
                            Markup.visit_count_row if item.absolute else Markup.visit_rate_row
                        ),
                        QSizeF(
                            headerWidth,
                            self.parent().rowHeight(row)
                        )
                    )
                    item.draw(p, rect, False)
                elif item is None:
                    pass
                else:
                    raise NotImplementedError(f'{type(item)} row: {row}')

                start_pixel += self.parent().rowHeight(row)
            except NoItemException:
                print('no item', row)

    def isHighlighted(self, row):
        return (self.row_clicked != -1 and self.row_clicked == row) or (self.row_clicked == -1 and self.hovered == row)

    def draw_item(self, p: QPainter, item, student, row, width, started_point):
        height = self.parent().rowHeight(row)

        rect = QRectF(started_point[0],
                      started_point[1] - self.parent().verticalOffset(),
                      width, height)

        p.fillRect(rect, self.get_color(item, row))

        p.setPen(self.textPen)
        if self.show_with_group_name:
            text = f"{names_of_groups(student.groups)} {item.text()}"
        else:
            text = item.text()
        p.drawText(rect, Qt.AlignLeft, text)

        p.setPen(self.border_pen)
        p.drawRect(rect)

    def get_color(self, item, row):
        if row == self.row_clicked:
            return Color.primary_dark
        if isinstance(item, StudentHeaderItem):
            if item.have_card():
                rect_color = self.no_card_color
            else:
                rect_color = self.primary_color
        else:
            rect_color = self.primary_color
        return rect_color

    def find_item(self, pos: QPoint) -> (QTableWidgetItem, int):
        def find_row(target_y):
            if target_y > Markup.visit_rate_row:
                return Markup.visit_rate_row_index
            elif target_y > Markup.visit_count_row:
                return Markup.visit_count_row_index
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

    def changes(self, row):
        self.model().headerDataChanged.emit(Qt.Vertical, row - 1, row + 1)
        self.viewport().repaint()
