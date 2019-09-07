from collections import namedtuple
from typing import List

from PyQt5.QtCore import pyqtSlot, Qt, pyqtSignal
from PyQt5.QtGui import QPalette, QColor
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QApplication, QLayout

from Client.MyQt.Widgets import QImageWidget
from Client.MyQt.Widgets.LoadData import Step
from Client.src.src import done_img


class QStepsWidget(QWidget):
    condition = namedtuple('condition', ['image', 'label', 'step'])

    completed = pyqtSignal(bool)

    def __init__(self, steps: List[Step], parent=None):
        super().__init__(parent)

        super_layout = QVBoxLayout()

        self.header = QLabel("Шаги выполнения:")
        super_layout.addWidget(self.header, alignment=Qt.AlignTop | Qt.AlignHCenter, stretch=1)

        self.main_layout = QVBoxLayout()
        self.main_layout.setAlignment(Qt.AlignVCenter)
        super_layout.addLayout(self.main_layout, stretch=9)

        self.items: List[QWidget] = list()
        self.map = dict()

        self._load_steps(steps)

        self.setLayout(super_layout)
        palette = QPalette()
        palette.setColor(QPalette.Background, QColor(200, 200, 200))
        self.setAutoFillBackground(True)
        self.setPalette(palette)

    def _load_steps(self, steps):
        for step in steps:
            row_layout = QHBoxLayout()
            row_layout.setAlignment(Qt.AlignTop)
            image = QImageWidget(done_img)
            image.setVisible(step.completed)
            sp = image.sizePolicy()
            sp.setRetainSizeWhenHidden(True)
            image.setSizePolicy(sp)

            label = QLabel(step.description)
            label.setToolTip(step.tooltip)

            row_layout.addWidget(image)
            row_layout.addWidget(label)

            self.map[step] = self.condition(image, label, step)

            self.items.extend((row_layout, image, label))
            self.main_layout.addLayout(row_layout)

    def _clear(self):
        for item in self.items:
            if isinstance(item, QWidget):
                self.main_layout.removeWidget(item)
            elif isinstance(item, QLayout):
                self.main_layout.removeItem(item)
            else:
                raise NotImplementedError()
            item.deleteLater()

        self.items = list()
        self.map = dict()
        QApplication.processEvents()

    @pyqtSlot('PyQt_PyObject', name='on_steps_changes')
    def on_steps_changes(self, new_steps):
        self._clear()
        self._load_steps(new_steps)

    @pyqtSlot('PyQt_PyObject', name='on_step')
    def on_step(self, step):
        self.map[step].image.setVisible(True)
        step.completed = True

        if all(map(lambda x: x.completed, self.map.keys())):
            self.completed.emit(True)

    @pyqtSlot('PyQt_PyObject', name='on_revoke_step')
    def on_revoke_step(self, step):
        self.map[step].image.setVisible(False)
        step.completed = False

        self.completed.emit(False)
