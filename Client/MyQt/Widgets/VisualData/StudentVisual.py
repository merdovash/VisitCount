from collections import defaultdict
from itertools import chain
from typing import List, Dict
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QVBoxLayout, QHBoxLayout, QLabel, QFormLayout, QCheckBox, QComboBox
from PyQtPlot.BarWidget import QBarGraphWidget
from PyQtPlot.Plot import PlotWidget

from Client.MyQt.Widgets import QSeparator
from Client.MyQt.Widgets.ComboBox.SemesterComboBox import GroupComboBox, StudentComboBox
from Client.MyQt.Widgets.VisualData import _VisualData
from DataBase2 import Lesson, Student, Visitation, Professor, Discipline
from Domain.functools.Format import agree_to_gender, agree_to_number


class StudentVisual(_VisualData):
    name = "Студенты"
    description = "Группировка статистики посещений по группам"
    group_by = ""

    def __init__(self, user, flags=None, *args, **kwargs):
        super().__init__(flags, *args, **kwargs)

        main_layout = QVBoxLayout()

        selector_layout = QHBoxLayout()

        group_box = GroupComboBox(self)
        student_box = StudentComboBox(self)
        self.plot_type_box = QComboBox()
        self.plot_type_box.addItems(["Интервальный (по неделям)", "Распределения"])

        group_box.current_changed.connect(student_box.on_parent_change)

        def plot_for_student(lessons: List[Lesson], student: Student):
            if student is not None:
                def replot():
                    visitations = defaultdict(lambda: defaultdict(list))
                    visited = 0
                    completed = 0
                    for lesson in lessons:
                        if lesson.completed:
                            completed += 1
                            visit = Visitation.get(user.session(), student_id=student.id, lesson_id=lesson.id)
                            if visit:
                                visitations[lesson.discipline][self.group(lesson)].append(1)
                                visited += 1
                            else:
                                visitations[lesson.discipline][self.group(lesson)].append(0)

                    def interval():
                        plot_layout.removeWidget(self.plot)
                        self.plot.deleteLater()

                        self.plot = QBarGraphWidget()
                        max_item = 1
                        for discipline, data in visitations.items():
                            if discipline_map[discipline].isChecked():
                                discipline_data = {group: round(sum(i) * 100 / len(i)) if len(i) > 0 else 0 for group, i
                                                   in
                                                   data.items()}
                                if max(data.keys())> max_item:
                                    max_item = max(data.keys())
                                self.plot.add_plot(discipline_data, discipline.name)
                        self.plot.vertical_ax.set_ticks(range(100))
                        self.plot.horizontal_ax.set_ticks(range(max(max_item, 18)))
                        self.plot.vertical_ax.set_label("Посещения, %")
                        self.plot.horizontal_ax.set_label("Номер недели")
                        self.plot.set_tooltip_func(
                            lambda col, val, name:
                            f"Студент {student}"
                            f"\nпосетил дисциплину {name}"
                            f"\nна {col} неделе"
                            f"\n{val}% занятий")

                        plot_layout.insertWidget(0, self.plot, stretch=9)

                    def distribution():
                        plot_layout.removeWidget(self.plot)
                        self.plot.deleteLater()

                        self.plot = PlotWidget()
                        plot_layout.insertWidget(0, self.plot, stretch=9)
                        max_index = 0
                        for discipline, groups in visitations.items():
                            keys = sorted(groups.keys())
                            if len(keys) > max_index:
                                max_index = len(keys)
                            data: Dict[int, int] = {}
                            for index, key in enumerate(keys):
                                visit = sum([sum(groups[k]) for k in keys[:index+1]])
                                total = index + 1
                                data[index+1] = round(visit / total * 100)

                            self.plot.add_plot(data, discipline.name)
                        self.plot.horizontal_ax.set_ticks(range(max_index))
                        self.plot.vertical_ax.set_ticks(range(100))
                        self.plot.vertical_ax.set_label("Посещения, %")
                        self.plot.horizontal_ax.set_label("Номер занятия")

                    total_visit_rate = round(100 * visited / completed) if completed > 0 else 0
                    last_completed_lesson = max(list(filter(lambda x: x.completed, lessons)),
                                                key=lambda x: x.date) if completed else min(lessons,
                                                                                            key=lambda x: x.date)

                    total_info_label.setText(
                        f"На дату {last_completed_lesson.date}\n"
                        f"Проведено {completed} {agree_to_number('занятие', completed)} из {len(lessons)};\n"
                        f"{student}\n{agree_to_gender('посетил', student.first_name)} {visited} "
                        f"{agree_to_number('занятие', visited)} из {completed} ({total_visit_rate}%)")

                    discipline_info_layout.addWidget(QLabel("Дисциплины:"))
                    self.remove_all_rows(discipline_info_layout)
                    discipline_map: Dict[Discipline, QCheckBox] = {}
                    for discipline in visitations:
                        check_box = QCheckBox()
                        check_box.setChecked(True)
                        discipline_map[discipline] = check_box
                        professors = Professor.of(list(filter(lambda lesson: lesson.discipline == discipline, lessons)))
                        professors_names = ""
                        for professor in professors:
                            professors_names += "\t" + professor.full_name() + "\n"
                        discipline_info_layout.addRow(check_box,
                                                      QLabel(f"{discipline.name}\nПреподаватели:\n{professors_names}"))

                        check_box.stateChanged.connect(replot)

                    if self.plot_type_box.currentIndex() == 0:
                        interval()
                    elif self.plot_type_box.currentIndex() == 1:
                        distribution()

                self.plot_type_box.disconnect()
                plot_layout.removeWidget(self.plot)
                self.plot.deleteLater()
                self.plot_type_box.currentIndexChanged.connect(replot)

                replot()
            else:
                pass

        student_box.current_changed.connect(plot_for_student)

        selector_layout.addWidget(QLabel('Группа'), alignment=Qt.AlignRight)
        selector_layout.addWidget(group_box)

        selector_layout.addWidget(QLabel('Студент'), alignment=Qt.AlignRight)
        selector_layout.addWidget(student_box)

        selector_layout.addWidget(QLabel('Тип представления'), alignment=Qt.AlignRight)
        selector_layout.addWidget(self.plot_type_box)

        plot_layout = QHBoxLayout()

        info_layout = QVBoxLayout()
        total_info_label = QLabel()
        discipline_info_layout = QFormLayout()

        info_layout.addWidget(total_info_label, stretch=1, alignment=Qt.AlignTop)
        info_layout.addWidget(QSeparator(Qt.Horizontal), alignment=Qt.AlignTop)
        info_layout.addLayout(discipline_info_layout, stretch=1)

        main_layout.addLayout(selector_layout)

        self.plot = QBarGraphWidget()
        plot_layout.addWidget(self.plot)
        plot_layout.addLayout(info_layout)

        main_layout.addLayout(plot_layout)
        self.setLayout(main_layout)

        group_box.loads(user)

    def group(self, lesson: Lesson):
        if self.plot_type_box.currentIndex() == 0:
            return lesson.week
        elif self.plot_type_box.currentIndex() == 1:
            return lesson.date
