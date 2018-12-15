from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont
from PyQt5.QtWidgets import QVBoxLayout, QHBoxLayout, QLabel

from Client.MyQt.QtMyStatusBar import QStatusMessage
from Client.MyQt.Table import VisitSection
from Client.MyQt.Window.Main import Selector
from Domain.functools.Format import format_name


class UI_TableWindow:
    def setupUi(self, widget):
        layout = QVBoxLayout(widget)

        info_layout = QHBoxLayout()

        professor_label = QLabel(
            format_name(widget.professor)
        )
        professor_label.setFont(QFont('Calibri', 20))

        self.info_label = QStatusMessage()

        info_layout.addWidget(professor_label, alignment=Qt.AlignLeft)
        info_layout.addWidget(self.info_label, alignment=Qt.AlignRight)

        layout.addLayout(info_layout, stretch=1)

        self.table = VisitSection(widget.program)
        self.selector = Selector(widget.program)

        layout.addWidget(self.selector, alignment=Qt.AlignTop, stretch=1)

        layout.addWidget(self.table, stretch=90)

        widget.setLayout(layout)
