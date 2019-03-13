from typing import Type, List

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QComboBox, QLabel, QPushButton

from Client.MyQt.Widgets.ComboBox.CheckComboBox import CheckableComboBox
from Client.MyQt.Widgets.ComboBox.SemesterComboBox import SemesterComboBox
from Client.MyQt.Widgets.ExtendedComboBox import ExtendedCombo
from Client.MyQt.Widgets.QLoadingIndicator import QtWaitingSpinner
from Client.MyQt.Widgets.VisualData.Graph import MyMplCanvas
from Client.MyQt.utils import simple_show
from DataBase2 import Discipline, Professor, Group, Student, _DBObject, Faculty, Department, Semester


class BisitorMPLWidget(QWidget):
    def __init__(self, user=None, flags=None):
        super().__init__(flags)
        with open('Client/src/style.qss', 'r') as style_file:
            self.setStyleSheet(style_file.read())
        data_groups: List[Type[_DBObject]] = [Student, Group, Professor, Discipline, Faculty, Department, Semester]
        plot_types = {
            "Посещения по неделям": 'bar_week',
            'Распределение': 'distribution',
            "Посещения по дням недели": "bar_weekday",
            "Посещения по занятиям": "bar_lesson",
            "Гистограма": 'hist',
            "Итоговое (по алфавиту)": 'total_alphabetic',
            "Итоговое (по возрастанию)": 'total_rated'
        }
        self.items = []

        main_layout = QVBoxLayout()

        selector_layout = QHBoxLayout()

        data_selector = QComboBox()
        selector_layout.addWidget(QLabel('Данные по'), alignment=Qt.AlignVCenter | Qt.AlignRight)
        selector_layout.addWidget(data_selector)

        item_selector = CheckableComboBox(with_all=True)
        item_selector_label = QLabel()
        # selector_layout.addWidget(item_selector_label, alignment=Qt.AlignVCenter | Qt.AlignRight)
        selector_layout.addWidget(item_selector)

        semester_selector = SemesterComboBox()
        selector_layout.addWidget(QLabel('за'), alignment=Qt.AlignVCenter | Qt.AlignRight)
        selector_layout.addWidget(semester_selector)
        semester_selector.loads(user)

        group_by_selector = QComboBox()
        selector_layout.addWidget(QLabel('группированные по'), alignment=Qt.AlignVCenter | Qt.AlignRight)
        selector_layout.addWidget(group_by_selector)

        plot_type_selector = QComboBox()
        plot_type_selector.addItems(plot_types.keys())
        selector_layout.addWidget(QLabel('Тип'))
        selector_layout.addWidget(plot_type_selector)

        show_btn = QPushButton('Построить')
        show_btn.setEnabled(False)
        selector_layout.addWidget(show_btn)

        def update_item_selector(index):
            item_selector.clear()
            self.items = data_groups[index].of(user, sort=lambda x: x.full_name())
            item_selector.setItems(self.items)
            item_selector_label.setText(data_groups[index].__name__)
            show_btn.setEnabled(True)

        def update_semester_selector(items):
            print('update', items)
            semester_selector.clear()
            new_semesters = Semester.of(items)
            semester_selector.addItems(new_semesters)

        def update_group_by_slector(index):
            group_by_selector.clear()
            group_by_selector.addItems([s.__name__ if i != index else 'нет' for i, s in enumerate(data_groups)])

        data_selector.currentIndexChanged.connect(update_item_selector)
        item_selector.currentChanged.connect(update_semester_selector)
        data_selector.currentIndexChanged.connect(update_group_by_slector)

        main_layout.addLayout(selector_layout)

        self.plot = QWidget()

        main_layout.addWidget(self.plot, stretch=99)

        data_selector.addItems([s.__name__ for s in data_groups])

        def show():
            self.plot.deleteLater()
            main_layout.removeWidget(self.plot)
            print('show', item_selector.current())
            self.plot = MyMplCanvas(
                item_selector.current(),
                data_groups[group_by_selector.currentIndex()].of,
                plot_types[plot_type_selector.currentText()],
                semester=semester_selector.current())

            main_layout.addWidget(self.plot)

        show_btn.clicked.connect(show)

        self.setLayout(main_layout)


if __name__ == '__main__':
    simple_show(BisitorMPLWidget, user=Professor.get(id=1))
