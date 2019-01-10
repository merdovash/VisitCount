import sys
from math import cos, sin
from operator import xor
from random import randint
from typing import List

from PyQt5.QtCore import QRect, Qt, QPoint
from PyQt5.QtGui import QPainter, QColor, QFont, QMouseEvent
from PyQt5.QtWidgets import QWidget, QApplication, QMainWindow

TOP = 0
RIGHT = 1
BOTTOM = 2
LEFT = 3


class _Plot:
    def __init__(self, data, parent):
        self.data = data
        self.parent = parent
        self.margin = parent._cal_margin

        self._width = 0.75
        self._nested_width = 0
        self._color = QColor(255, 128, 0)
        self._offset = 0

    def paint(self, painter):
        width = self.parent.width()
        height = self.parent.height()
        top, right, bottom, left = self.margin()

        for bar, h in self.data.items():
            x_pos = left + self.parent.horizontal_ax.ticks().index(bar) * self.parent.horizontal_ax.tick_interval()
            rect = QRect(
                x_pos + (1 - self.real_width() + self.offset() * 2) * self.parent.horizontal_ax.tick_interval() / 2,
                self.parent.horizontal_ax.y_pos(),
                self.parent.horizontal_ax.tick_interval() * self.width(),
                -h * self.parent.vertical_ax.tick_interval())
            if self.parent.mouse_pos() is not None \
                    and rect.contains(self.parent.mouse_pos().x(), self.parent.mouse_pos().y()):
                text_rect = QRect(int(self.parent.mouse_pos().x())+15, int(self.parent.mouse_pos().y()), 20, 20)
                self.parent._show_tooltip(text_rect, str(h), bar)
            painter.fillRect(
                rect,
                self.color()
            )


    def set_width(self, val):
        self._width = val

    def width(self):
        if self._nested_width == 0:
            return self._width
        else:
            return self._nested_width

    def set_color(self, val):
        self._color = val

    def color(self):
        return self._color

    def set_offset(self, val):
        self._offset = val

    def offset(self):
        return self._offset

    def set_nested_width(self, val):
        self._nested_width = val

    def real_width(self):
        return self._width


class _Axis:
    def __init__(self, parent):
        self.width = parent.width
        self.height = parent.height
        self.margin = parent._cal_margin

        self._ticks = None
        self._tick_count = None
        self._tick_width = 6
        self._tick_interval = None
        self._ticks_margin = 0
        self._tick_rotation = 0
        self._y_pos = None
        self._size = None

    def paint(self, painter):
        raise NotImplementedError()

    def set_ticks(self, val):
        self._ticks = val

    def ticks(self):
        return self._ticks

    def _set_tick_interval(self, val):
        self._tick_interval = val

    def tick_interval(self):
        return self._tick_interval

    def set_tick_margin(self, val):
        self._ticks_margin = val

    def tick_margin(self):
        return self._ticks_margin

    def y_pos(self):
        return self._y_pos

    def _set_y_pos(self, val):
        self._y_pos = val

    def _set_size(self, val):
        self._size = val

    def size(self):
        return self._size

    def _set_tick_count(self, val):
        self._tick_count = val

    def tick_count(self):
        return self._tick_count

    def tick_rotation(self):
        return self._tick_rotation

    def set_tick_rotation(self, val):
        self._tick_rotation = val

    def tick_width(self):
        return self._tick_width


class _HorizontalAxis(_Axis):
    def __init__(self, parent):
        super().__init__(parent)

    def paint(self, painter):
        width = self.width()
        height = self.height()
        top, right, bottom, left = self.margin()

        self._set_tick_count(len(self._ticks))
        self._set_size(width - left - right)
        self._set_tick_interval(self.size() / self.tick_count())
        self._set_y_pos(height - bottom)
        for i in range(self.tick_count()):
            x_pos = left + (i + 0.5) * self.tick_interval()
            painter.drawLine(x_pos, self.y_pos() - self.tick_width() / 2, x_pos, self.y_pos() + self.tick_width() / 2)

            if self.tick_rotation() != 0:
                painter.translate(x_pos, self.y_pos() + self.tick_width() / 2 + 4)
                painter.rotate(-self.tick_rotation())
                painter.translate(-x_pos, -(self.y_pos() + self.tick_width() / 2 + 4))
                painter.drawText(
                    QRect(
                        x_pos - self.tick_interval() / 2 + self.tick_margin() * cos(self.tick_rotation()) - 20,
                        self.y_pos() + (self.tick_width() / 2 + 4) * cos(
                            self.tick_rotation()) - self.tick_margin() * sin(self.tick_rotation()),
                        50,
                        30),
                    xor(Qt.AlignHCenter, Qt.AlignVCenter),
                    str(self.ticks()[i])
                )
                painter.resetTransform()
            else:
                painter.drawText(
                    QRect(
                        x_pos - self.tick_interval() / 2,
                        self.y_pos() + self.tick_width() / 2 + 4 + self.tick_margin(),
                        self.tick_interval(),
                        20),
                    Qt.AlignHCenter,
                    str(self._ticks[i])
                )


class _VerticalAxis(_Axis):
    def __init__(self, parent):
        super().__init__(parent)

    def paint(self, painter):
        width = self.width()
        height = self.height()
        top, right, bottom, left = self.margin()

        painter.drawLine(left, top, left, height - bottom)
        painter.drawLine(left, height - bottom, width - right, height - bottom)

        self._set_tick_count(self.ticks()[-1] - self.ticks()[0] + 1)
        self._set_size(height - bottom - bottom)
        self._set_tick_interval(self.size() / self.tick_count())
        for i in range(self.tick_count()):
            if i in self.ticks():
                y_pos = (height - bottom) - i * self.tick_interval()
                painter.drawLine(left - self.tick_width() / 2, y_pos, left + self.tick_width() / 2, y_pos)

                painter.drawText(
                    QRect(0, y_pos - 10, left - self.tick_width() / 2 - 4, 20),
                    xor(Qt.AlignVCenter, Qt.AlignRight),
                    str(i))


class QBarGraphWidget(QWidget):
    colors = [QColor(255, 128, 0), QColor(0, 128, 255), QColor(128, 255, 0), QColor(0, 255, 128)]

    def __init__(self, bars, heights, flags, *args, **kwargs):
        assert len(bars) == len(heights)
        super().__init__(flags, *args, **kwargs)

        self.bars = bars
        self.heights = heights

        self._map = [{bars[i]: heights[i] for i in range(len(bars))}]

        self.vertical_ax = _VerticalAxis(self)

        if len(heights):
            self.vertical_ax.set_ticks(range(0, max(heights) + 1, max(int(max(heights) / 20), 1)))
        else:
            self.vertical_ax.set_ticks([0, 1])

        self.horizontal_ax = _HorizontalAxis(self)
        self.horizontal_ax.set_ticks(bars)

        self.plots: List[_Plot] = [_Plot(d, self) for d in self._map]

        self.margin = (0.1, 0.1, 0.1, 0.1)

        self.color = QColor(255, 128, 0)
        self.bg_color = QColor(255, 255, 255)

        self.item_color = QColor(255, 128, 0)

        self.item_width = 0.75

        self.font = QFont()
        self.font.setPixelSize(20)

        self.setMouseTracking(True)
        self._mouse_pos = QPoint(0, 0)

        self.tooltips = []
        self.tooltip_func = lambda text, bar: text

    def mouse_pos(self):
        return self._mouse_pos

    def mouseMoveEvent(self, event: QMouseEvent):
        if (self._mouse_pos - event.localPos()).manhattanLength() > 3:
            self._mouse_pos = event.localPos()
            self.repaint()
            print('set', self._mouse_pos)

    def update_data(self, i, bars, heights):
        self._map[i] = {bars[i]: heights[i] for i in range(len(bars))}
        self.plots[i] = _Plot(self._map[i], self)

        self.repaint()

    def _show_tooltip(self, rect, text, bar):
        self.tooltips.append((rect, text, bar))

    def paintEvent(self, QPaintEvent):
        painter = QPainter()
        painter.begin(self)

        painter.setFont(self.font)

        width = self.width()
        height = self.height()

        painter.fillRect(0, 0, width, height, self.bg_color)

        self.vertical_ax.paint(painter)
        self.horizontal_ax.paint(painter)

        for plot in self.plots:
            plot.paint(painter)

        while len(self.tooltips):
            rect, text, bar = self.tooltips.pop()
            res = self.tooltip_func(text, bar)
            if res is not None:
                painter.drawText(rect, xor(Qt.AlignHCenter, Qt.AlignVCenter), res)

        painter.end()

    def addPlot(self, plot):
        self.plots.append(_Plot(plot, self))
        print(self.plots)
        for index, p in enumerate(self.plots):
            p.set_nested_width(p.real_width() / len(self.plots))
            p.set_color(self.colors[index])
            if index > 0:
                p.set_offset(sum(map(lambda x: x.width(), self.plots[:index])))

    def _cal_margin(self):
        return self.height() * self.margin[TOP], self.width() * self.margin[RIGHT], self.height() * self.margin[BOTTOM], \
               self.width() * self.margin[LEFT]


if __name__ == '__main__':
    from Client.MyQt.Widgets.Graph.HistogramWidget import Histogram

    app = QApplication(sys.argv)

    window = QMainWindow()
    hist = Histogram([randint(1995, 2014) for _ in range(randint(20, 50))], window)

    hist.horizontal_ax.set_ticks(list(range(1990, 2018)))
    hist.horizontal_ax.set_tick_margin(20)
    hist.horizontal_ax.set_tick_rotation(30)
    hist.addPlot([randint(1995, 2014) for _ in range(randint(20, 50))])
    hist.addPlot([randint(1995, 2014) for _ in range(randint(20, 50))])

    window.setCentralWidget(hist)

    window.show()

    sys.exit(app.exec_())
