import sys

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QPushButton, QApplication, QHBoxLayout

from Client.MyQt.Widgets import QSeparator
from Client.MyQt.Widgets.VisualData import _VisualData
from DataBase2 import _DBPerson, Professor

import Client.MyQt.Widgets.VisualData.GroupVisual
import Client.MyQt.Widgets.VisualData.StudentVisual
import Client.MyQt.Widgets.VisualData.DisciplineVisual
import Client.MyQt.Widgets.VisualData.ProfessorVisual

class VisualWidget(QWidget):
    def __init__(self, user: _DBPerson, flags=None, *args, **kwargs):
        super().__init__(flags, *args, **kwargs)
        self.setMinimumSize(500, 500)
        self.setWindowTitle("СПбГУТ Учет посещений: Просмотр данных")

        main_layout = QVBoxLayout()

        title_layout = QVBoxLayout()

        title_layout.addWidget(QLabel("Ниже вы можете выбрать главный критерий группировки"), alignment=Qt.AlignHCenter)
        title_layout.addWidget(QSeparator(Qt.Horizontal))

        main_layout.addLayout(title_layout, stretch=1)

        for cls in _VisualData.subclasses():
            layout = QHBoxLayout()
            btn = QPushButton(cls.name)
            label = QLabel(cls.description)

            def show(cls):
                def __show__():
                    self.close()
                    cls(user).show()
                return __show__

            btn.clicked.connect(show(cls))

            layout.addWidget(btn, alignment=Qt.AlignHCenter, stretch=1)
            layout.addWidget(label, alignment=Qt.AlignLeft, stretch=6)

            main_layout.addLayout(layout, stretch=1)

        self.setLayout(main_layout)


if __name__ == '__main__':
    app = QApplication(sys.argv)

    widget = VisualWidget(Professor.get(id=1))
    widget.show()

    sys.exit(app.exec_())
