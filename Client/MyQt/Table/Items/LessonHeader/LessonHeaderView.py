from typing import Tuple

from PyQt5.QtCore import Qt, QRectF, QPoint, QEvent
from PyQt5.QtGui import QPainter, QColor, QPen, QCursor
from PyQt5.QtWidgets import QHeaderView, QTableWidgetItem, QMenu

import Date
from Client.MyQt.ColorScheme import Color
from Client.MyQt.Time import from_time_to_index
from DataBase2 import Lesson


class LessonHeaderItem(QTableWidgetItem):
    def __init__(self, lesson: Lesson, *__args):
        super().__init__(*__args)

        self.lesson = lesson

        dt = lesson.date

        self.month = "0,Январь,Февраль,Март,Апрель,Май,Июнь,Июль,Август,Сентябрь,Октябрь,Ноябрь,Декабрь".split(',')[
            dt.month]
        self.day = str(dt.day)
        self.week = str(dt.isocalendar()[1] - Date.start_week())
        self.weekday = ["пн", "вт", "ср", "чт", "пт", "сб", "вс"][dt.weekday()]
        self.number = str(from_time_to_index(dt))
        self.type = ['Л', 'лр', 'п'][lesson.type]


class LessonHeaderView(QHeaderView):
    border_pen = QPen(QColor(187, 187, 187))
    border_pen.setWidthF(0.5)

    background_color = QColor(234, 234, 234)

    def __init__(self):
        super().__init__(Qt.Horizontal)

        self.item_width = 15
        self.item_heigth = 19

        self.text_offset = 2, 16

        self.setFixedHeight(self.item_heigth * 5)

        self.setContextMenuPolicy(Qt.CustomContextMenu)
        self.customContextMenuRequested.connect(self.contextMenu)

        self.hovered = -1

        self.installEventFilter(self)

    def paintEvent(self, QPaintEvent):
        current_month = None
        current_week = None

        start = True

        p = QPainter(self.viewport())

        offset = self.parent().horizontalOffset()

        start_pixel = -1

        month_start = start_pixel, 0
        week_start = start_pixel, 1

        month_count = 0
        week_count = 1

        for col in range(self.parent().columnCount()):
            item = self.parent().horizontalHeaderItem(col)
            item_width = self.parent().columnWidth(col)
            if isinstance(item, LessonHeaderItem):
                if start:
                    current_month = item.month
                    current_week = item.week

                    start = False

                if current_month != item.month:
                    self.draw_item(p, current_month, month_start, start_pixel - month_start[0], offset,
                                   col - month_count <= self.hovered < col)
                    current_month = item.month
                    month_start = (start_pixel, 0)
                    month_count = 0

                if current_week != item.week:
                    self.draw_item(p, current_week, week_start, start_pixel - week_start[0], offset,
                                   col - week_count <= self.hovered < col)
                    current_week = item.week
                    week_start = (start_pixel, 1)
                    week_count = 0

                self.draw_item(p, item.day, (start_pixel, 2), item_width, offset, self.hovered == col)
                self.draw_item(p, item.weekday, (start_pixel, 3), item_width, offset, self.hovered == col)
                self.draw_item(p, item.number, (start_pixel, 4), item_width, offset, self.hovered == col)
                self.draw_item(p, item.type, (start_pixel, 5), item_width, offset, self.hovered == col)

                week_count += 1
                month_count += 1

            start_pixel += self.parent().columnWidth(col)
        else:
            self.draw_item(p, current_month, month_start, start_pixel - month_start[0], offset,
                           self.parent().columnCount() - month_count <= self.hovered < self.parent().columnCount())
            self.draw_item(p, current_week, week_start, start_pixel - week_start[0], offset,
                           self.parent().columnCount() - week_count <= self.hovered < self.parent().columnCount())

    def draw_item(self, painter: QPainter, text: str, index: Tuple[int, int], width: int, offset: int, hovered: bool):
        x = index[0]
        y = index[1] * self.item_heigth
        rect = QRectF(x - offset, y, width, self.item_heigth)
        painter.fillRect(rect, Color.secondary_accent if hovered else self.background_color)

        painter.setPen(QPen(QColor(0, 0, 0), ))
        painter.drawText(rect, Qt.AlignCenter, text)

        painter.setPen(self.border_pen)
        painter.drawRect(rect)

    def contextMenu(self, point: QPoint):
        menu = QMenu()
        pos = QCursor.pos()

        item, _ = self.find_item(pos)
        if item.lesson.completed:
            menu.addAction("Отменить факт проведения занятия")
        menu.addAction("Перенести занятие")
        menu.exec(pos)

    def eventFilter(self, object, event: QEvent, *args, **kwargs):
        if event.type() == 10 or event.type() == 183:
            _, col = self.find_item(QCursor.pos())
            self.set_hovered(col)

            return True

        elif event.type() == 11:
            self.set_hovered(-1)

            return True

        elif event.type() == QEvent.MouseButtonPress:
            pass

        return False

    def find_item(self, pos: QPoint) -> (LessonHeaderItem, int):
        x = pos.x()
        current = self.pos().x() - self.parent().horizontalOffset() + self.parent().pos().x()
        for col in range(self.parent().columnCount()):
            width = self.parent().columnWidth(col)
            if current <= x <= current + width:
                return self.parent().horizontalHeaderItem(col), col
            current += width
        raise IndexError("click is out of range")

    def set_hovered(self, index):
        if index != self.hovered:
            self.hovered = index if index is not None else -1
            self.model().headerDataChanged.emit(Qt.Horizontal, 0, self.parent().columnCount())
