from operator import xor

from PyQt5.QtCore import Qt, QRectF
from PyQt5.QtGui import QPainter, QPen, QColor, QMouseEvent, QFont
from PyQt5.QtWidgets import QLineEdit

from Client.MyQt.ColorScheme import Color


class LineEdit(QLineEdit):
    default_pen = QPen(QColor(0, 0, 0))

    hovered_pen = QPen(default_pen)
    hovered_pen.setColor(Color.primary)
    hovered_pen.setWidth(2)

    default_font = QFont()
    default_font.setPointSize(10)

    def __init__(self, *__args):
        super().__init__(*__args)

        self.press_start = -1
        self.press_end = -1

    def paintEvent(self, QPaintEvent):
        p = QPainter(self)

        rect = QRectF(0, 0, self.width(), self.height())

        # p.fillRect(rect, Color.secondary)

        p.setPen(self.default_pen if not self.hasFocus() else self.hovered_pen)
        p.drawLine(0, rect.height() - 3, rect.width(), rect.height() - 3)

        p.setPen(self.default_pen)
        p.setFont(self.default_font)

        p.fillRect(QRectF(self.press_start, 0, self.press_end, self.height() - 3), Color.secondary)
        p.drawText(QRectF(0, 0, self.width(), self.height() - 3), xor(Qt.AlignBottom, Qt.AlignLeft), self.text())

    def mousePressEvent(self, event: QMouseEvent):
        self.press_start = event.pos().x()

    def mouseReleaseEvent(self, event: QMouseEvent):
        self.press_end = event.pos().x()
