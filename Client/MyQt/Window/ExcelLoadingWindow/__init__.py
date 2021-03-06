from typing import List, Dict

from PyQt5.QtCore import QUrl, pyqtSignal, pyqtSlot
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QProgressBar, QPushButton


class ExcelLoadingWidget(QWidget):
    exit = pyqtSignal()

    def __init__(self, files: List[QUrl], parent=None, *args, **kwargs):
        QWidget.__init__(self, parent, *args, **kwargs)

        # self.setWindowFlags(Qt.WindowStaysOnTopHint)

        self.setMinimumSize(300, 300)

        self.files = files

        layout = QVBoxLayout(self)

        self.loading: Dict[QUrl, QProgressBar] = {}
        self.loading_status: Dict[QUrl, bool] = {}

        for file in files:
            layout.addWidget(QLabel(f'{file.fileName()}'))
            self.loading[file] = QProgressBar()
            self.loading_status[file] = False
            self.loading[file].setRange(0, 100)
            self.loading[file].valueChanged.connect(lambda value: self.on_change(value, file))
            layout.addWidget(self.loading[file])

        self.end_button = QPushButton('Завершить')
        self.end_button.setVisible(False)
        self.exit.connect(lambda: self.end_button.setVisible(True))

        layout.addWidget(self.end_button)

        self.setLayout(layout)

    @pyqtSlot(name='run')
    def run(self):
        for file in self.files:
            raise NotImplementedError()

    def on_change(self, value, file):
        self.loading_status[file] = value >= 100

        if all(self.loading_status.values()):
            self.end_button.setVisible(True)

    def showAsChild(self, *args):
        self.show()
        self.raise_()
        self.run()
