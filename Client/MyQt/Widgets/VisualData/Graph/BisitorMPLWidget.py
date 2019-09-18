from typing import Type, List

from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtWidgets import QVBoxLayout, QComboBox, QLabel, QPushButton, QTabWidget, QGridLayout, \
    QCheckBox

from Client.MyQt.Widgets import BisitorWidget
from Client.MyQt.Widgets.VisualData.Graph import MyMplCanvas
from Client.MyQt.utils import simple_show
from DataBase2 import Professor, Student, DBObject, Semester, IRoot


class SettingWidget(BisitorWidget):
    accept = pyqtSignal('PyQt_PyObject', 'PyQt_PyObject', 'PyQt_PyObject', 'PyQt_PyObject')

    def __init__(self, user: DBObject, *args, **kwargs):
        from Client.MyQt.Widgets.ComboBox import QMCheckedComboBox, QMComboBox

        super().__init__(*args, **kwargs)
        data_groups: List[Type[IRoot or DBObject]] = sorted(IRoot.__subclasses__(), key=lambda x: x.__type_name__)
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

        main_layout = QGridLayout()

        data_selector = QMComboBox(IRoot)
        main_layout.addWidget(QLabel('Данные по'), 0, 0)
        main_layout.addWidget(data_selector, 0, 1, 1, 2)

        item_selector = QMCheckedComboBox(self, with_all=True, type_=Student)
        item_selector_label = QLabel()
        # selector_layout.addWidget(item_selector_label, alignment=Qt.AlignVCenter | Qt.AlignRight)
        main_layout.addWidget(QLabel('Выбор'), 0, 3)
        main_layout.addWidget(item_selector, 0, 4, 1, 2)

        semester_selector = QMCheckedComboBox(self, False, Semester)
        main_layout.addWidget(QLabel('за'), 1, 0)
        main_layout.addWidget(semester_selector, 1, 1, 1, 2)
        semester_selector.loads(user)

        group_by_selector = QMComboBox(IRoot)
        group_by_selector.setEnabled(False)
        main_layout.addWidget(QLabel('Группировать'), 2, 0)
        group_by_checkbox = QCheckBox('включить')
        group_by_checkbox.stateChanged.connect(group_by_selector.setEnabled)
        main_layout.addWidget(group_by_checkbox, 2, 1, 1, 2)
        main_layout.addWidget(QLabel('по'), 2, 3)
        main_layout.addWidget(group_by_selector, 2, 4, 1, 2)

        plot_type_selector = QComboBox()

        main_layout.addWidget(QLabel('Тип'), 3, 0)
        main_layout.addWidget(plot_type_selector, 3, 1, 1, 2)

        description = QLabel()
        description.setWordWrap(True)
        main_layout.addWidget(QLabel('Описание'), 3, 3)
        main_layout.addWidget(description, 3, 4, 3, 2, Qt.AlignTop)

        plot_type_selector.currentTextChanged.connect(lambda x: description.setText(plot_types[x][1]))

        for i in range(6):
            main_layout.setRowStretch(i, 1)
        show_btn = QPushButton('Построить')
        show_btn.setEnabled(False)
        main_layout.addWidget(show_btn, 5, 2, 1, 2)

        def update_item_selector(index):
            item_selector.setEngine(data_selector.current())
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
            group_by_selector.addItems([s for i, s in enumerate(data_groups) if i != index])

        data_selector.currentIndexChanged.connect(update_item_selector)
        item_selector.currentChanged.connect(update_semester_selector)
        data_selector.currentIndexChanged.connect(update_group_by_slector)

        data_selector.addItems([s for s in data_groups])

        def show():
            self.accept.emit(
                item_selector.current(),
                group_by_selector.current() if group_by_checkbox.isChecked() else data_selector.current(),
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

        self.tabs = QTabWidget()
        self.tabs.setTabsClosable(True)
        self.tabs.tabCloseRequested.connect(lambda x: self.tabs.removeTab(x) if x != 0 else None)
        main_layout.addWidget(self.tabs)

        setting_widget = SettingWidget(user)
        self.tabs.addTab(setting_widget, "Настройки")

        def on_accept(items, group_by, plot_type, semester):
            plot = MyMplCanvas(
                items,
                group_by,
                plot_type,
                semester=semester)
            self.tabs.addTab(plot, 'График')
            self.tabs.setCurrentWidget(plot)

        setting_widget.accept.connect(on_accept)

        self.setLayout(main_layout)


if __name__ == '__main__':
    simple_show(BisitorMPLWidget, user=Professor.get(id=1))
