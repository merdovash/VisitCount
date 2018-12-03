from typing import List, Dict

from PyQt5.QtCore import QUrl
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QProgressBar, QPushButton

from Client.MyQt.Window.interfaces import IChildWindow
from Domain.ExcelLoader import ExcelVisitationLoader


class ExcelLoadingWidget(QWidget, IChildWindow):
    def __init__(self, files: List[QUrl], program, parent=None, *args, **kwargs):
        QWidget.__init__(self, parent, *args, **kwargs)
        IChildWindow.__init__(self)

        self.files = files

        self.excel_loader = ExcelVisitationLoader(program)

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
        self.end_button.clicked.connect(self.closeSelf)
        self.end_button.setVisible(False)

        layout.addWidget(self.end_button)

        self.setLayout(layout)

    def run(self):
        for file in self.files:
            self.excel_loader.read(file, progress_bar=self.loading[file])

    def on_change(self, value, file):
        self.loading_status[file] = value >= 100

        if all(self.loading_status.values()):
            self.end_button.setVisible(True)

    def showAsChild(self, *args):
        self.show()
        self.run()
