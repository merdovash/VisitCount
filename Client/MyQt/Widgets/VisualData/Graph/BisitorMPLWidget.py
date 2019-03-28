from typing import Type, List

from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QComboBox, QLabel, QPushButton, QTabWidget

from Client.MyQt.Widgets import BisitorWidget
from Client.MyQt.Widgets.ComboBox import MCheckedComboBox
from Client.MyQt.Widgets.ComboBox.CheckComboBox import CheckableComboBox
from Client.MyQt.Widgets.ComboBox.SemesterComboBox import SemesterComboBox, StudentComboBox
from Client.MyQt.Widgets.VisualData.Graph import MyMplCanvas
from Client.MyQt.utils import simple_show
from DataBase2 import Discipline, Professor, Group, Student, _DBObject, Faculty, Department, Semester, _DBRoot
from Domain.Plotting.View import BokehPlot


class SettingWidget(BisitorWidget):
    accept = pyqtSignal('PyQt_PyObject', 'PyQt_PyObject', 'PyQt_PyObject', 'PyQt_PyObject')

    def __init__(self, user: _DBObject, *args, **kwargs):
        super().__init__(*args, **kwargs)
        data_groups: List[Type[_DBRoot or _DBObject]] = sorted(_DBRoot.__subclasses__(), key=lambda x: x.type_name)
        plot_types = {
            "Посещения по неделям": ('bar_week', "Показывает уровень посещений на каждой неделе"),
            'Распределение': ('distribution', "Показывает итоговый уровень посещений на дату"),
            "Посещения по дням недели": ("bar_weekday", "Показывает уровень посещений по дням недели"),
            "Посещения по занятиям": ("bar_lesson", "Показывает уровень посещения по времени начала начала занятия"),
            "Гистограма": ('hist', "Показывает частоту каждого уровня посещений"),
            "Итоговое (по алфавиту)": ('total_alphabetic', "Итоговое посещений на данный момент, отсортированное в алфавитном пордке"),
            "Итоговое (по возрастанию)": ('total_rated', "Итоговое посещений на данный момент, отсортированное в порядке возрастания процента посещений"),
            "Общий тренд": ('scatter', "Показывает итоговое посещение на данный момент и график тренда"),
            "Отклонения по дням": ("deviation", "Показывает изменение процента посещений относительно предыдущего дня")
        }
        self.items = []

        main_layout = QVBoxLayout()

        item_select_layout = QHBoxLayout()
        main_layout.addLayout(item_select_layout)

        data_selector = QComboBox()
        item_select_layout.addWidget(QLabel('Данные по'), alignment=Qt.AlignVCenter | Qt.AlignLeft, stretch=1)
        item_select_layout.addWidget(data_selector, stretch=2)

        item_selector = MCheckedComboBox(self, with_all=True, type_=StudentComboBox())
        item_selector_label = QLabel()
        # selector_layout.addWidget(item_selector_label, alignment=Qt.AlignVCenter | Qt.AlignRight)
        item_select_layout.addWidget(item_selector, stretch=6)

        semester_select_layout = QHBoxLayout()
        main_layout.addLayout(semester_select_layout)

        semester_selector = MCheckedComboBox(self, False, SemesterComboBox())
        semester_select_layout.addWidget(QLabel('за'), alignment=Qt.AlignVCenter | Qt.AlignLeft, stretch=1)
        semester_select_layout.addWidget(semester_selector, stretch=8)
        semester_selector.loads(user)

        group_by_layout = QHBoxLayout()
        main_layout.addLayout(group_by_layout)

        group_by_selector = QComboBox()
        group_by_layout.addWidget(QLabel('группированные по'), alignment=Qt.AlignVCenter | Qt.AlignLeft, stretch=1)
        group_by_layout.addWidget(group_by_selector, stretch=8)

        plot_type_layout = QHBoxLayout()
        main_layout.addLayout(plot_type_layout)

        plot_type_selector = QComboBox()

        plot_type_layout.addWidget(QLabel('Тип'), alignment=Qt.AlignVCenter | Qt.AlignLeft, stretch=1)
        plot_type_layout.addWidget(plot_type_selector, stretch=8)

        description_layout = QHBoxLayout()
        description = QLabel()
        description_layout.addWidget(QLabel('Описание'), stretch=1)
        description_layout.addWidget(description, stretch=8)
        main_layout.addLayout(description_layout)

        plot_type_selector.currentTextChanged.connect(lambda x: description.setText(plot_types[x][1]))

        button_layout = QHBoxLayout()
        main_layout.addLayout(button_layout)

        show_btn = QPushButton('Построить')
        show_btn.setEnabled(False)
        button_layout.addWidget(show_btn, alignment=Qt.AlignBottom)

        def update_item_selector(index):
            item_selector.clear()
            self.items = data_groups[index].of(user, sort=lambda x: x.full_name())
            item_selector.set_items(self.items)
            item_selector_label.setText(data_groups[index].__name__)
            show_btn.setEnabled(True)

        def update_semester_selector(items):
            semester_selector.clear()
            semester_selector.loads(items)

        def update_group_by_slector(index):
            group_by_selector.clear()
            group_by_selector.addItems([s.type_name if i != index else 'нет' for i, s in enumerate(data_groups)])

        data_selector.currentIndexChanged.connect(update_item_selector)
        item_selector.currentChanged.connect(update_semester_selector)
        data_selector.currentIndexChanged.connect(update_group_by_slector)

        self.plot = QWidget()

        main_layout.addWidget(self.plot, stretch=99)

        data_selector.addItems([s.type_name for s in data_groups])

        def show():
            self.accept.emit(
                item_selector.current(),
                data_groups[group_by_selector.currentIndex()],
                plot_types[plot_type_selector.currentText()][0],
                semester_selector.current()
            )

        show_btn.clicked.connect(show)

        self.setLayout(main_layout)

        plot_type_selector.addItems(plot_types.keys())


class BisitorMPLWidget(BisitorWidget):
    def __init__(self, user=None):
        super().__init__()

        main_layout = QVBoxLayout()

        tabs = QTabWidget()
        tabs.setTabsClosable(True)
        tabs.tabCloseRequested.connect(lambda x: tabs.removeTab(x) if x != 0 else None)
        main_layout.addWidget(tabs)

        setting_widget = SettingWidget(user)
        tabs.addTab(setting_widget, "Настройки")

        def on_accept(items, group_by, plot_type, semester):
            if plot_type == 'distribution':
                plot = BokehPlot.distribution(user=items, group=group_by, semester=semester)
                plot.create()
                widget = plot.widget()

            else:
                widget = MyMplCanvas(
                    items,
                    group_by,
                    plot_type,
                    semester=semester)
            tabs.addTab(widget, 'График')
            tabs.setCurrentWidget(widget)

        setting_widget.accept.connect(on_accept)

        self.setLayout(main_layout)


if __name__ == '__main__':
    simple_show(BisitorMPLWidget, user=Professor.get(id=1))
