from typing import Tuple

from PyQt5.QtCore import Qt, QRectF, QPoint, QEvent, QSizeF
from PyQt5.QtGui import QPainter, QColor, QPen, QHelpEvent, QMouseEvent
from PyQt5.QtWidgets import QHeaderView, QTableWidgetItem, QMenu, QToolTip

import Date
from Client import IProgram
from Client.MyQt.ColorScheme import Color
from Client.MyQt.Table.Control import VisitTableControl
from Client.MyQt.Table.Items import IDraw
from Client.MyQt.Table.Section import Markup
from Client.MyQt.Time import from_time_to_index
from Client.MyQt.Widgets.LessonDateChanger import LessonDateChanger
from DataBase2 import Lesson


class PercentHeaderItem(IDraw, QTableWidgetItem):
    def __init__(self, orientation, max_count=None, absolute=False, *__args):
        super().__init__(*__args)
        self.absolute = absolute

        if absolute:
            if orientation == Qt.Vertical:
                self.setText(f'Итого\n из {max_count}')
            else:
                self.setText(f'Итого из {max_count}')
        else:
            if orientation == Qt.Vertical:
                self.setText(f'Итого,\n %')
            else:
                self.setText(f'Итого, %')

    def draw(self, painter, rect, highlighted=False):
        painter.fillRect(rect, self.get_color(highlighted))

        painter.setPen(self.textPen)
        painter.drawText(rect, Qt.AlignCenter, self.text())

        painter.setPen(self.border_pen)
        painter.drawRect(rect)

    def get_color(self, highlighted):
        return Color.to_accent(Color.secondary_light) if highlighted else Color.secondary_light


class LessonHeaderItem(QTableWidgetItem):
    def __init__(self, lesson: Lesson, program: IProgram, *__args):
        super().__init__(*__args)
        self.program = program
        self.lesson = lesson

        dt = lesson.date

        self.date = dt

        self.month = "0,Январь,Февраль,Март,Апрель,Май,Июнь,Июль,Август,Сентябрь,Октябрь,Ноябрь,Декабрь".split(',')[
            dt.month]
        self.day = str(dt.day)
        self.week = str(dt.isocalendar()[1] - Date.start_week())
        self.weekday = ["пн", "вт", "ср", "чт", "пт", "сб", "вс"][dt.weekday()]
        self.number = str(from_time_to_index(dt))
        self.type = ['Л', 'лр', 'п'][lesson.type]

    def unstart(self):
        self.lesson.completed = False

        self.tableWidget().viewport().repaint()

    def move_lesson(self):
        self.calendar = LessonDateChanger(self.program, self.date, self.lesson)
        self.calendar.show()


class LessonHeaderView(QHeaderView):
    class Header(int):
        MONTH = 0
        WEEK_NUMBER = 1
        DAY = 2
        WEEKDAY = 3
        LESSON = 4
        LESSONTYPE = 5

        COUNT = 6

    border_pen = QPen(QColor(187, 187, 187))
    border_pen.setWidthF(0.5)

    background_color = QColor(234, 234, 234)

    def __init__(self, parent=None):
        super().__init__(Qt.Horizontal, parent)

        self.item_width = 35
        self.item_height = 19

        self.text_offset = 2, 16

        self.setFixedHeight(self.item_height * 6)

        self.setContextMenuPolicy(Qt.CustomContextMenu)
        self.customContextMenuRequested.connect(self.contextMenu)

        self.hovered = -1

        self.installEventFilter(self)

        self.setSectionResizeMode(QHeaderView.Fixed)
        self.setMouseTracking(True)

        self._show = [True in range(LessonHeaderView.Header.COUNT)]
        self.show = [self.set_show_row(i, None) for i in range(LessonHeaderView.Header.COUNT)]

        self.show_cross = True

    def set_show_cross(self, b):
        assert isinstance(b, bool), f'{b} is not a bool'
        self.show_cross = b

    def set_show_row(self, i, b):
        def _show_run(b):
            self._show[i] = b

        if b is None:
            return _show_run
        else:
            self._show[i] = b

    def paintEvent(self, QPaintEvent):
        try:
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

            for col in range(len(self.parent().lessons)):
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
                else:
                    raise NotImplementedError(item)

                start_pixel += self.parent().columnWidth(col)
            else:
                self.draw_item(p, current_month, month_start, start_pixel - month_start[0], offset,
                               self.parent().columnCount() - month_count <= self.hovered < self.parent().columnCount())
                self.draw_item(p, current_week, week_start, start_pixel - week_start[0], offset,
                               self.parent().columnCount() - week_count <= self.hovered < self.parent().columnCount())

            for col in range(self.parent().columnCount() - 2, self.parent().columnCount()):
                item = self.parent().horizontalHeaderItem(col)

                if isinstance(item, PercentHeaderItem):
                    width = self.parent().columnWidth(col)
                    rect = QRectF(
                        QPoint(
                            Markup.visit_count_col if item.absolute else Markup.visit_rate_col,
                            0),
                        QSizeF(
                            width,
                            self.height()
                        ))
                    item.draw(p, rect, self.isHighlighted(col))
        except (TypeError, NotImplementedError):
            pass

    def isHighlighted(self, col):
        return col == self.hovered

    def draw_item(self, painter: QPainter, text: str, index: Tuple[int, int], width: int, offset: int, hovered: bool):
        x = index[0]
        y = index[1] * self.item_height
        rect = QRectF(x - offset, y, width, self.item_height)
        painter.fillRect(rect, Color.secondary_accent if hovered and self.show_cross else self.background_color)

        painter.setPen(QPen(QColor(0, 0, 0), ))
        painter.drawText(rect, Qt.AlignCenter, text)

        painter.setPen(self.border_pen)
        painter.drawRect(rect)

    def contextMenu(self, point: QPoint):
        menu = QMenu()
        # pos = point.pos

        item, _, _ = self.find_item(point)
        control: VisitTableControl = self.parent().getControl()
        if isinstance(item, LessonHeaderItem):
            if item.lesson.completed:
                menu.addAction("Отменить факт проведения занятия", item.unstart)
            menu.addAction("Перенести занятие", item.move_lesson)
            if control.isLessonStarted():
                menu.addAction('Завершить учет', lambda: control.end_lesson())
            elif control.currentLesson() != item.lesson:
                menu.addAction('Выбрать занятие', lambda: control.select_lesson(item.lesson))
            menu.exec(self.mapToGlobal(point))

    def mouseMoveEvent(self, event: QMouseEvent):
        try:
            _, col, _ = self.find_item(event.pos())

            self.set_hovered(col, True)

            QToolTip.hideText()

        except:
            self.set_hovered(-1, True)

    def eventFilter(self, object, event: QEvent, *args, **kwargs):
        if event.type() == QEvent.ToolTip:
            pos = QHelpEvent(event).globalPos()
            item, col, row = self.find_item(QHelpEvent(event).pos())
            QToolTip.showText(pos, ['Месяц', 'Номер недели', 'День', 'День недели', 'Номер пары', 'Тип занятия'][row])
        if event.type() == QEvent.Scroll:
            return True

        return False

    def find_item(self, pos: QPoint) -> (LessonHeaderItem, int, int):
        def find_col(target_x):
            if target_x > Markup.visit_rate_col:
                return Markup.visit_rate_col_index
            elif target_x > Markup.visit_count_col:
                return Markup.visit_count_col_index
            else:
                current_x = - self.parent().horizontalOffset()

                for col in range(self.parent().columnCount()):
                    width = self.parent().columnWidth(col)
                    if current_x <= target_x <= current_x + width:
                        return col
                    current_x += width
                else:
                    return -1

        col = find_col(pos.x())
        row = pos.y() // self.item_height

        return self.parent().horizontalHeaderItem(col), col, row

    def set_hovered(self, index, pure=False):
        if index != self.hovered:
            self.hovered = index if index is not None else -1
            self.model().headerDataChanged.emit(Qt.Horizontal, 0, self.parent().columnCount())
        if pure:
            self.parent().set_hover(-1, index)
