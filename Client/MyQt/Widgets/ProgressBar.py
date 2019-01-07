from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QProgressBar, QApplication


class ProgressBar(QWidget):
    def __init__(self, flags, *args, **kwargs):
        super().__init__(flags, *args, **kwargs)

        layout = QVBoxLayout()

        self.label = QLabel()
        self.progress_bar = QProgressBar()

        layout.addWidget(self.label, alignment=Qt.AlignCenter)
        layout.addWidget(self.progress_bar)

        self.setLayout(layout)
        self.part = None
        self.base = 0

    def set_part(self, size, length, text):
        if self.part is None:
            self.current_tick = 0
            self.current_part_size = length
            self.current_tick_size = size/length
            self.text = text
            self.part = True
        else:
            raise ValueError('part is not over')

    def increment(self):
        if self.part is not None:
            self.current_tick += 1
            self.label.setText(f'{self.text}: {self.current_tick}/{self.current_part_size}')
            self.base += self.current_tick_size
            self.progress_bar.setValue(int(self.base))
            if self.current_tick == self.current_part_size:
                self.part = None
        else:
            raise ValueError('part is not set')

    def last(self):
        return 100-self.base

    def abord(self):
        self.part = None
        self.base = 0
        self.progress_bar.setValue(0)
        self.label.setText('Отмена')
