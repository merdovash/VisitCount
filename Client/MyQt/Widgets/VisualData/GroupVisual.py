from collections import defaultdict
from typing import List

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QApplication
from PyQtPlot.BarWidget import QBarGraphWidget

from Client.MyQt.Widgets.ComboBox.SemesterComboBox import GroupComboBox, SemesterComboBox
from Client.MyQt.Widgets.VisualData import _VisualData
from DataBase2 import Lesson, Group, Student, Visitation
from Domain.Structures import Vector
from Domain.Data import names_of_groups
from Domain.functools.Format import agree_to_number


class GroupVisual(_VisualData):
    name = "Группы"
    description = "Группировка статистики посещений по группам"
    group_by = Group

    def __init__(self, professor, flags=None, *args, **kwargs):
        super().__init__(flags, *args, **kwargs)

        main_layout = QVBoxLayout()

        selector_layout = QHBoxLayout()
        semester_box = SemesterComboBox()
        group_box = GroupComboBox(self)
        selector_layout.addWidget(QLabel('Семестр'), alignment=Qt.AlignRight)
        selector_layout.addWidget(semester_box)
        selector_layout.addWidget(QLabel("Группа"), alignment=Qt.AlignRight)
        selector_layout.addWidget(group_box)

        data_layout = QHBoxLayout()

        self.plot = QBarGraphWidget()
        data_layout.addWidget(self.plot, stretch=9)

        info_layout = QVBoxLayout()
        total_info_label = QLabel()
        info_layout.addWidget(total_info_label, alignment=Qt.AlignTop)

        main_layout.addLayout(selector_layout)
        main_layout.addLayout(data_layout)

        self.setLayout(main_layout)

        def plot_group(lessons: List[Lesson], groups: List[Group]):
            if len(groups) == 0:
                return
            data_layout.removeWidget(self.plot)
            self.plot.deleteLater()

            students = Student.of(groups)
            visitations = defaultdict(lambda: defaultdict(lambda: Vector(0, 0)))
            completed = 0
            total = 0
            max_week = 0
            for lesson in lessons:
                if lesson.completed:
                    completed += 1
                    visitations[lesson.discipline][lesson.week] += Vector(
                        len(list(set(Visitation.of(students)) & set(Visitation.of(lesson)))),
                        len(students)
                    )
                if lesson.week > max_week:
                    max_week = lesson.week

            self.plot = QBarGraphWidget()

            for discipline, data in visitations.items():
                self.plot.add_plot(
                    plot={week: round(value[0] * 100 / value[1]) if value[1] else 0 for week, value in data.items()},
                    name=discipline.name
                )

            self.plot.vertical_ax.set_ticks(range(100))
            self.plot.horizontal_ax.set_ticks(range(max_week))
            # self.plot.set_tooltip_func(
            #     lambda col, value, discipline_name:
            #     f"{agree_to_number('группа', len(groups))} {names_of_groups(groups)}\n"
            #     f"{agree_to_number('посетила', len(groups))} {value}% занятий\n"
            #     f"дисциплины {discipline_name}\n"
            #     f"на {col} неделе"
            # )

            data_layout.insertWidget(0, self.plot, stretch=9)

        group_box.current_changed.connect(plot_group)
        semester_box.current_changed.connect(group_box.on_parent_change)
        semester_box.loads(professor)
