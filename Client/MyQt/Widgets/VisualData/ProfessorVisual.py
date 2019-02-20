from collections import defaultdict
from typing import Any, List

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QVBoxLayout, QHBoxLayout, QLabel
from PyQtPlot.BarWidget import QBarGraphWidget

from Client.MyQt.Widgets.ComboBox.SemesterComboBox import SemesterComboBox, ProfessorComboBox
from Client.MyQt.Widgets.VisualData import _VisualData
from DataBase2 import Professor, Lesson, Visitation, Student
from Domain.Structures import NamedVector


class ProfessorVisual(_VisualData):
    name = "Преподаватель"
    description = "Просмотр статистики по преподавателям"
    group_by = Professor

    def __init__(self, user, flags=None, *args, **kwargs):
        super().__init__(flags, *args, **kwargs)

        main_layout = QVBoxLayout()

        selector_layout = QHBoxLayout()

        semester_combo = SemesterComboBox()
        professor_combo = ProfessorComboBox()
        selector_layout.addWidget(QLabel("Семестр"), alignment=Qt.AlignRight)
        selector_layout.addWidget(semester_combo)
        selector_layout.addWidget(QLabel("Преподаватель"), alignment=Qt.AlignRight)
        selector_layout.addWidget(professor_combo)

        main_layout.addLayout(selector_layout)

        data_layout = QHBoxLayout()

        self.plot = QBarGraphWidget()
        data_layout.addWidget(self.plot, stretch=9)

        info_layout = QVBoxLayout()
        data_layout.addLayout(info_layout, stretch=1)

        main_layout.addLayout(data_layout)

        self.setLayout(main_layout)

        def show_professor(lessons: List[Lesson], professor: Professor):
            def replot(data):
                data_layout.removeWidget(self.plot)
                self.plot.deleteLater()
                self.plot = QBarGraphWidget()
                self.plot.add_plot(data, name=professor.full_name())
                self.plot.vertical_ax.set_ticks(range(100))
                self.plot.horizontal_ax.set_ticks(range(max(18, max(data.keys()) if len(data) else 0)))
                data_layout.insertWidget(0, self.plot, stretch=9)

            visitations, total = self.calculate_visitations(lessons)
            data = {
                key: NamedVector.rate(v.visit, v.total)
                for key, v in visitations.items()
            }
            replot(data)

        professor_combo.current_changed.connect(show_professor)
        semester_combo.current_changed.connect(professor_combo.on_parent_change)
        semester_combo.loads(user)

    def group(self, lesson: Lesson) -> Any:
        return lesson.week
