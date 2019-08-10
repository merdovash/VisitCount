from PyQt5.QtCore import pyqtSignal
from PyQt5.QtGui import QPalette, QColor
from PyQt5.QtWidgets import QWidget, QColorDialog


class QColorPicker(QWidget):
    color_changed = pyqtSignal(bool)
    color_change = pyqtSignal('PyQt_PyObject')

    def __init__(self, color, default_color, name, flags=None, *args, **kwargs):
        super().__init__(flags, *args, **kwargs)
        self.default_color = default_color if isinstance(default_color, QColor) else QColor(default_color)
        self.name = name
        self.setFixedSize(50, 40)
        self._set_color(color if color else self.default_color)

    def mouseReleaseEvent(self, event):
        res = QColorDialog.getColor(self.color)
        if res.isValid():
            self._set_color(res)

    def reset_color(self):
        self._set_color(self.default_color)

    def _set_color(self, color):
        self.pal = QPalette()
        color = color if isinstance(color, QColor) else QColor(color)
        self.color = color
        self.pal.setColor(QPalette.Background, color)
        self.setAutoFillBackground(True)
        self.setPalette(self.pal)
        self.color_changed.emit(self.default_color != self.color)
        self.color_change.emit({
            'value': self.color,
            'name': self.name,
            'section': 'colors'
        })
