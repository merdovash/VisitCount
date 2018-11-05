from math import ceil

import matplotlib.pyplot as plt
import numpy as np
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QVBoxLayout, QComboBox, QLabel, \
    QHBoxLayout, QWidget, QFormLayout, QCheckBox
from matplotlib.backends.backend_qt5agg import \
    FigureCanvasQTAgg as FigureCanvas, \
    NavigationToolbar2QT as NavigationToolbar
# from Main.DataBase.GlobalStatistic import Statistic
from matplotlib.figure import Figure

from Client.IProgram import IProgram
from Client.MyQt.Widgets.HLine import HLine
from DataBase2 import Lesson, Student, Group, Discipline
from Domain.Aggregation import Column
from Domain.Data import names_of_groups


def show(graph_window_constructor, program: IProgram):
    def x():
        window = program.window
        if window.dialog is not None:
            # window.dialog.done(0)
            window.dialog = None
        dialog = graph_window_constructor(program)
        dialog.setStyleSheet(program.css)
        window.setDialog(graph_window_constructor(program))

    return x


class LessonData:
    def __init__(self, lesson: Lesson, param):
        self.lesson = lesson
        self.param = param
        self.visit = len(self.lesson.visitations)
        self.total = len(Student.of(lesson))

    def __repr__(self):
        return "(lesson: {}, param: {}, visit: {}/{})".format(self.lesson, self.param, self.visit, self.total)


class LessonAccumulator:
    TOTAL = 0
    VISIT = 1

    def __init__(self, r: range = None, lessons: list = None):
        # init base containers
        if r is not None:
            self.data = {i: [0, 0] for i in r}
        else:
            self.data = {}
        self.all = {}

        # allow to fill in constructor
        if lessons is not None:
            for l in lessons:
                self.add_lesson(l)

    def add_lesson(self, lesson: LessonData):
        if lesson.param not in self.data.keys():
            self.data[lesson.param] = [0, 0]
            self.all[lesson.param] = []
        self.data[lesson.param][LessonAccumulator.TOTAL] += lesson.total
        self.data[lesson.param][LessonAccumulator.VISIT] += lesson.visit
        self.all[lesson.param].append(lesson.visit * 100 / lesson.total)

    def get_data(self):
        total, visit = [], []
        for d in self.data:
            total.append(self.data[d][LessonAccumulator.TOTAL])
            visit.append(self.data[d][LessonAccumulator.VISIT])

        f = []
        for i in range(len(total)):
            if total[i] != 0:
                f.append(visit[i] * 100 / total[i])
            else:
                f.append(0)
        return f

    def get_hist_data(self):
        data = self.get_data()
        arr = []
        for i in range(len(data)):
            for j in range(int(ceil(data[i]))):
                arr.append(i)
        return arr

    def get_box_data(self):
        for x in self.all:
            print(x, self.all[x])
        return [np.array(self.all[x]) for x in self.all]

    def is_ready(self):
        return False


class QAnalysisDialog(QWidget):
    class DataType(int):
        WEEK = 1
        WEEK_DAY = 2

    plot_types = {
        0: dict(type='bar', xlabel=None, ylabel='Процент посещений'),
        1: dict(type='hist', xlabel='Процент посещений', ylabel='Количество занятий'),
    }

    # TODO destroy on exit (memory leak)
    def __init__(self, program: IProgram, parent=None):
        super().__init__(parent)
        self.setStyleSheet(program.css)
        self.program: IProgram = program

        self.setMinimumWidth(600)
        self.setMinimumHeight(600)

        # initialise plots variables
        self._ax = None
        self._gp = None

        # parameters
        self.count = None

        self.figure = plt.figure()
        self.canvas = FigureCanvas(Figure(figsize=(5, 3)))

        self._ax = self.canvas.figure.subplots()

        self.toolbar = NavigationToolbar(self.canvas, self)

        # init plot type selector
        combobox_layout = QHBoxLayout()

        self.plot_type_label = QLabel('Тип графика')

        self.combo_box = QComboBox()
        self.combo_box.setStyleSheet(program.css)
        self.combo_box.addItems("Столбчатая диаграмма,Гистограма".split(','))
        self.combo_box.currentIndexChanged.connect(self.draw)

        combobox_layout.addWidget(self.plot_type_label)
        combobox_layout.addWidget(self.combo_box)

        layout = QVBoxLayout()
        layout.addWidget(self.canvas)
        layout.addWidget(self.toolbar)

        layout.addLayout(combobox_layout)

        layout.addWidget(HLine())

        self.__init_control_panel__(layout)

        self.setLayout(layout)

    def refresh_data(self):
        raise NotImplementedError()

    def __init_control_panel__(self, layout):
        self.groups = {}
        self.disciplines = {}

        params_layout = QHBoxLayout()
        layout.addLayout(params_layout)

        group_layout = QFormLayout()
        for group in Group.of(self.program.professor, flat_list=True):
            def action(g):
                def a():
                    self.groups[g] = not self.groups[g]
                    self.refresh_data()
                    self.draw()

                return a

            check_box = QCheckBox()
            self.groups[group] = True
            check_box.setCheckState(Qt.Checked)
            check_box.stateChanged.connect(action(group))
            group_layout.addRow(names_of_groups(group), check_box)

        params_layout.addLayout(group_layout)

        discipline_layout = QFormLayout()
        for disc in Discipline.of(self.program.professor):
            def action(d):
                def a():
                    self.disciplines[d] = not self.disciplines[d]
                    self.refresh_data()
                    self.draw()

                return a

            check_box = QCheckBox()
            self.disciplines[disc] = True
            check_box.setCheckState(Qt.Checked)
            check_box.stateChanged.connect(action(disc))
            discipline_layout.addRow(disc.name, check_box)

        params_layout.addLayout(discipline_layout)

    def draw(self):
        # remove old and setup new
        self.ax().clear()

        index = self.combo_box.currentIndex()

        plot_legend = self.plot_types[index]

        kwargs = {'ylim': [0, 100] if index == 0 else None}

        self._draw(ax=self.ax(), plot_type=plot_legend['type'], **kwargs)

        if plot_legend['xlabel'] is not None:
            self.ax().set_xlabel(plot_legend['xlabel'])
        if plot_legend['ylabel'] is not None:
            self.ax().set_ylabel(plot_legend['ylabel'])

        # refresh canvas
        self.canvas.draw()

    def ax(self):
        return self._ax

    def _draw(self, plot_type, ax, **kwargs):
        self.get_data().plot(
            x=Column.date,
            y=Column.visit_rate,
            ax=ax,
            kind=plot_type,
            title='Посещения',
            **kwargs)
