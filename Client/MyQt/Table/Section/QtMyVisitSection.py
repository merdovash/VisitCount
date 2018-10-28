from PyQt5.QtCore import Qt, QPoint, QRectF, QEvent
from PyQt5.QtGui import QPainter, QPen, QColor, QCursor
from PyQt5.QtWidgets import QTableWidget, QAbstractItemView, QPushButton

from Client.MyQt.ColorScheme import Color
from Client.MyQt.Table import StudentHeaderView, VisitItem, PercentItem
from Client.MyQt.Table.Items import AbstractContextItem
from Client.MyQt.Table.Items.LessonHeader.LessonHeaderView import LessonHeaderView


class CornerWidget(QPushButton):
    def __init__(self, *args):
        super().__init__(*args)

        self.setStyleSheet("CornerWidget{ background-color:#ededed}")

    def paintEvent(self, QPaintEvent):
        p = QPainter(self)

        rect = QRectF(0, 0, self.width(), self.height())

        p.fillRect(rect, Color.secondary)
        p.drawRect(rect)
        p.drawLine(0, 0, self.width(), self.height())


class VisitSection(QTableWidget):
    border_pen = QPen(Color.secondary_dark)
    border_pen.setWidthF(0.5)

    textPen = QPen(Color.text_color)

    def __init__(self, *__args):
        super().__init__(*__args)

        self.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
        self.setEditTriggers(QAbstractItemView.NoEditTriggers)

        self.setContextMenuPolicy(Qt.CustomContextMenu)
        self.customContextMenuRequested.connect(self.table_right_click)

        self.setVerticalHeader(StudentHeaderView())

        self.setHorizontalHeader(LessonHeaderView())
        self.horizontalHeader().setVisible(True)

        self.setCornerWidget(CornerWidget())

        self.row_hovered = -1
        self.col_hovered = -1

        self.row_height = 20
        self.col_width = 35

        self.installEventFilter(self)

        self.setMouseTracking(True)

        self.show_cross = True

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
            real_pos = QCursor.pos()
            item.show_context_menu(real_pos)

    def mouseMoveEvent(self, event):
        try:
            item, row, col = self.find_item(event.pos())
            self.set_hover(row, col)
        except IndexError:
            self.set_hover(-1, -1)

    def paintEvent(self, QPaintEvent):
        p = QPainter(self.viewport())

        started_point = [-1, -1]

        for col, l in enumerate(self.parent().lessons):
            width = self.columnWidth(col)
            for row, st in enumerate(self.parent().students):
                item = self.item(row, col)
                self.draw_item(p, item, row, col, started_point)
                started_point[1] += self.rowHeight(row)

            for row in range(len(self.parent().students), len(self.parent().students) + 2):
                item = self.item(row, col)
                if isinstance(item, PercentItem):
                    item.refresh()
                self.draw_item(p, item, row, col, started_point)
                started_point[1] += self.rowHeight(row)
            else:
                started_point[1] = -1

            started_point[0] += width

    def draw_item(self, p: QPainter, item: VisitItem or PercentItem, row, col, started_point):
        width = self.columnWidth(col)
        height = self.rowHeight(row)

        rect = QRectF(started_point[0] - self.horizontalOffset(), started_point[1] - self.verticalOffset(),
                      width, height)

        p.fillRect(rect, self.get_color(item, row, col))

        p.setPen(self.textPen)
        p.drawText(rect, Qt.AlignCenter, item.text())

        p.setPen(self.border_pen)
        p.drawRect(rect)

    def get_color(self, item, row, col):
        if isinstance(item, VisitItem):
            if self.show_cross and (row == self.row_hovered or col == self.col_hovered):
                return Color.to_accent(QColor(item.get_color()))
            else:
                return QColor(item.get_color())
        else:
            if self.show_cross and (row == self.row_hovered or col == self.col_hovered):
                return Color.secondary_light_accent
            else:
                return Color.secondary_light

    def eventFilter(self, object, event):
        if event.type() == QEvent.MouseMove:
            item, row, col = self.find_item(event.pos())
            self.set_hover(row, col)
            return True

        return False

    def find_item(self, pos: QPoint):
        def find_row(target_y):
            current_y = - self.verticalOffset()

            for row in range(self.rowCount()):
                height = self.rowHeight(row)
                if current_y <= target_y <= current_y + height:
                    return row

                current_y += height
            else:
                return -1

        def find_col(target_x):
            current_x = - self.horizontalOffset()

            for col in range(self.columnCount()):
                width = self.columnWidth(col)
                if current_x <= target_x <= current_x + width:
                    return col
                current_x += width
            else:
                return -1

        row, col = find_row(pos.y()), find_col(pos.x())
        return self.item(row, col), row, col

    def set_hover(self, row, col):
        if self.row_hovered != row \
                or self.col_hovered != col \
                or (row == -1 and self.row_hovered != -1) \
                or (col == -1 and self.col_hovered != -1):
            self.row_hovered = row
            self.col_hovered = col

            self.verticalHeader().set_hovered(row)
            self.horizontalHeader().set_hovered(col)

            self.model().dataChanged.emit(self.model().index(0, 0),
                                          self.model().index(self.columnCount() - 1, self.rowCount() - 1))

            self.viewport().repaint()

    def set_row_hover(self, row):
        self.set_hover(row, self.col_hovered)

    def set_col_hover(self, col):
        self.set_hover(self.row_hovered, col)

    def select_current_lesson(self, lesson):
        self.parent().set_current_lesson(lesson)

    def switch_show_table_cross(self):
        self.show_cross = not self.show_cross

    # def eventFilter(self, obj, event):
    #    if event.type() != QtCore.QEvent.Paint or not isinstance(obj, QtWidgets.QAbstractButton):
    #        return False

#
#    # Paint by hand (borrowed from QTableCornerButton)
#    opt = QtWidgets.QStyleOptionHeader()
#    opt.initFrom(obj)
#    styleState = QtWidgets.QStyle.State_None
#    if obj.isEnabled():
#        styleState |= QtWidgets.QStyle.State_Enabled
#    if obj.isActiveWindow():
#        styleState |= QtWidgets.QStyle.State_Active
#    if obj.isDown():
#        styleState |= QtWidgets.QStyle.State_Sunken
#    opt.state = styleState
#    opt.rect = obj.rect()
#    # This line is the only difference to QTableCornerButton
#    opt.text = obj.text()
#    opt.position = QtWidgets.QStyleOptionHeader.OnlyOneSection
#    painter = QtWidgets.QStylePainter(obj)
#    painter.drawControl(QtWidgets.QStyle.CE_Header, opt)
#
#    return True
#
