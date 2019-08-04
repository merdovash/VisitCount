from typing import List

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QWidget, QHBoxLayout, QLabel

from Client.MyQt.Widgets.ComboBox.MComboBox import QMComboBox
from DataBase2 import _DBPerson


class QMSelector(QWidget):
    def __init__(self, items: List[QMComboBox], user: _DBPerson, flags=None):
        assert all(isinstance(item, QMComboBox) for item in items)
        super().__init__(flags)

        main_layout = QHBoxLayout()
        for index, item in enumerate(items):
            main_layout.addWidget(QLabel(item.label), alignment=Qt.AlignRight | Qt.AlignVCenter, stretch=1)
            main_layout.addWidget(item, stretch=3)
            if index > 0:
                items[index - 1].current_changed.connect(item.on_parent_change)

        items[0].loads(user)

        self.setLayout(main_layout)