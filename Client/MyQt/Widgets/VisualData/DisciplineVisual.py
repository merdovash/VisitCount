from collections import defaultdict
from typing import List, Dict, Any

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QVBoxLayout, QHBoxLayout, QLabel, QFormLayout, QComboBox
from PyQtPlot.BarWidget import QBarGraphWidget

from Client.MyQt.Widgets import QSeparator
from Client.MyQt.Widgets.ComboBox.SemesterComboBox import DisciplineComboBox, SemesterComboBox
from Client.MyQt.Widgets.VisualData import _VisualData
from DataBase2 import Discipline, Lesson, Professor, Student, Visitation
from Domain.Structures import Vector, NamedVector


class DisciplineVisual(_VisualData):
    name = "Дисциплина"
    description = "Группировка данных о песещениях в разрезе дисциплин"
    group_by = Discipline

    plot: QBarGraphWidget

    def __init__(self, user, flags=None, *args, **kwargs):
        super().__init__(flags, *args, **kwargs)

        main_layout = QVBoxLayout()

        selector_layout = QHBoxLayout()
        semester_combo = SemesterComboBox()
        discipline_combo = DisciplineComboBox(self)
        group_by_combo = QComboBox()
        self.group_by_combo = group_by_combo
        selector_layout.addWidget(QLabel('Семестер'), alignment=Qt.AlignRight)
        selector_layout.addWidget(semester_combo)
        selector_layout.addWidget(QLabel("Дисциплина"), alignment=Qt.AlignRight)
        selector_layout.addWidget(discipline_combo)
        selector_layout.addWidget(QLabel("Группировать"), alignment=Qt.AlignRight)
        selector_layout.addWidget(group_by_combo)

        main_layout.addLayout(selector_layout)

        data_layout = QHBoxLayout()

        self.plot = QBarGraphWidget()
        data_layout.addWidget(self.plot)

        info_layout = QVBoxLayout()
        info_layout.addWidget(QLabel())
        info_layout.addWidget(QSeparator(Qt.Horizontal))
        info_layout.addLayout(QFormLayout())

        data_layout.addLayout(info_layout, stretch=1)

        def show_discipline(lessons: List[Lesson], discipline: Discipline):
            def replot(visitations: Dict[Any, int]):
                data_layout.removeWidget(self.plot)
                self.plot.deleteLater()
                self.plot = QBarGraphWidget()
                self.plot.add_plot(visitations, name=discipline.name)
                self.plot.vertical_ax.set_ticks(range(100))
                if all([isinstance(i, int) for i in visitations.keys()]):
                    self.plot.horizontal_ax.set_ticks(range(max(18, max(visitations.keys()) if len(visitations) else 0)))
                else:
                    self.plot.horizontal_ax.set_ticks(visitations.keys())
                data_layout.insertWidget(0, self.plot, stretch=9)

            visitations = defaultdict(lambda: NamedVector(visit=0, total=0))
            completed = defaultdict(int)
            total = NamedVector(visit=0, total=0)
            for lesson in lessons:
                if lesson.completed:
                    completed[lesson.professor] += 1
                    lesson_data = NamedVector(
                        visit=len(Visitation.of(lesson)),
                        total=len(Student.of(lesson))
                    )
                    visitations[self.group(lesson)] += lesson_data
                    total += lesson_data

            data = self.prepare_data(visitations)
            self.apply_group_info(info_layout, discipline, total)

            replot(data)

        main_layout.addLayout(data_layout)

        self.setLayout(main_layout)
        discipline_combo.current_changed.connect(show_discipline)
        semester_combo.current_changed.connect(discipline_combo.on_parent_change)
        semester_combo.loads(user)

        group_by_combo.addItem("нет (суммарное)")
        group_by_combo.addItem("по преподавателям")

    def group(self, lesson):
        if self.group_by_combo.currentIndex()==0:
            return lesson.week
        elif self.group_by_combo.currentIndex()==1:
            return Professor.of(lesson)[0]

    def apply_group_info(self, layout, discipline, total_visit):
        form_layout = layout.itemAt(2)
        self.remove_all_rows(form_layout)

        layout.itemAt(0).widget().setText(f"Всего посещений {total_visit.visit} из {total_visit.total} "
                                 f"({NamedVector.rate(total_visit.visit, total_visit.total)}%)")

    def prepare_data(self, visitations):
        data = {
            group: NamedVector.rate(v.visit, v.total)
            for group, v in visitations.items()
        }
        return data
