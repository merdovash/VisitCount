from collections import defaultdict
from itertools import chain
from typing import List, Dict

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QVBoxLayout, QHBoxLayout, QLabel, QFormLayout, QCheckBox
from PyQtPlot.BarWidget import QBarGraphWidget

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

        group_box.current_changed.connect(student_box.on_parent_change)

        def plot_for_student(lessons: List[Lesson], student: Student):
            if student is not None:
                def replot():
                    plot_layout.removeWidget(self.plot_widget)
                    self.plot_widget.deleteLater()

                    self.plot_widget = QBarGraphWidget()
                    for discipline, data in visitations.items():
                        if discipline_map[discipline].isChecked():
                            discipline_data = {week: round(sum(i) * 100 / len(i)) if len(i) > 0 else 0 for week, i in
                                               data.items()}
                            self.plot_widget.add_plot(discipline_data, discipline.name)
                    self.plot_widget.vertical_ax.set_ticks(range(100))
                    self.plot_widget.horizontal_ax.set_ticks(range(max_week))
                    self.plot_widget.set_tooltip_func(
                        lambda col, val, name:
                        f"Студент {student}"
                        f"\nпосетил дисциплину {name}"
                        f"\nна {col} неделе"
                        f"\n{val}% занятий")

                    plot_layout.insertWidget(0, self.plot_widget, stretch=9)

                plot_layout.removeWidget(self.plot_widget)
                self.plot_widget.deleteLater()

                visitations = defaultdict(lambda: defaultdict(list))
                visited = 0
                completed = 0
                for lesson in lessons:
                    if lesson.completed:
                        completed += 1
                        visit = Visitation.get(user.session(), student_id=student.id, lesson_id=lesson.id)
                        if visit:
                            visitations[lesson.discipline][lesson.week].append(1)
                            visited += 1
                        else:
                            visitations[lesson.discipline][lesson.week].append(0)
                try:
                    max_week = max(18, max(chain.from_iterable([item.keys() for item in visitations.values()])) + 1)
                except ValueError:
                    max_week = 18

                total_visit_rate = round(100 * visited / completed) if completed > 0 else 0
                last_completed_lesson = max(list(filter(lambda x: x.completed, lessons)),
                                            key=lambda x: x.date) if completed else min(lessons, key=lambda x: x.date)

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

                replot()
            else:
                pass

        student_box.current_changed.connect(plot_for_student)

        selector_layout.addWidget(QLabel('Группа'), alignment=Qt.AlignRight)
        selector_layout.addWidget(group_box)

        selector_layout.addWidget(QLabel('Студент'), alignment=Qt.AlignRight)
        selector_layout.addWidget(student_box)

        plot_layout = QHBoxLayout()

        info_layout = QVBoxLayout()
        total_info_label = QLabel()
        discipline_info_layout = QFormLayout()

        info_layout.addWidget(total_info_label, stretch=1, alignment=Qt.AlignTop)
        info_layout.addWidget(QSeparator(Qt.Horizontal), alignment=Qt.AlignTop)
        info_layout.addLayout(discipline_info_layout, stretch=1)

        main_layout.addLayout(selector_layout)

        self.plot_widget = QBarGraphWidget()
        plot_layout.addWidget(self.plot_widget)
        plot_layout.addLayout(info_layout)

        main_layout.addLayout(plot_layout)
        self.setLayout(main_layout)

        group_box.loads(user)
