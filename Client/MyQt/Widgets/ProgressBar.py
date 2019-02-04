from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QProgressBar, QApplication, QPushButton


class ProgressBar(QWidget):
    finish = pyqtSignal()

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

        self.finish_label = QLabel(kwargs.get('finish_text', 'Завершено'))
        self.finish_button = QPushButton('Закрыть')
        self.finish = self.finish_button.clicked

    def set_part(self, size, length, text):
        if self.part is None:
            if length > 0:
                self.current_tick = 0
                self.current_part_size = length
                self.current_tick_size = size / length
                self.text = text
                self.part = True
            else:
                self.base += size
                self.progress_bar.setValue(self.base)
            QApplication.processEvents()
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
            QApplication.processEvents()
        else:
            raise ValueError('part is not set')

    def last(self):
        return 100 - self.base

    def abord(self):
        self.part = None
        self.base = 0
        self.progress_bar.setValue(0)
        self.label.setText('Отмена')

    def on_finish(self, msg):
        self.layout().removeWidget(self.label)
        self.finish_label.setText(msg)
        self.layout().removeWidget(self.progress_bar)
        self.layout().addWidget(self.finish_label)
        self.layout().addWidget(self.finish_button)
        self.progress_bar.deleteLater()
        self.label.deleteLater()
        QApplication.processEvents()
        self.finish.emit()
