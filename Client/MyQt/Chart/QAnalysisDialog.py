import traceback
from math import ceil

import matplotlib.pyplot as plt
import numpy as np
from PyQt5.QtGui import QFont
from PyQt5.QtWidgets import QDialog, QVBoxLayout, QComboBox, QLabel, QHBoxLayout
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas

# from Main.DataBase.GlobalStatistic import Statistic
from Client.Domain.Data import students_of_groups
from Client.IProgram import IProgram
from DataBase2 import Lesson


def show(c, program: IProgram):
    def x():
        window = program.window
        try:
            if window.dialog is not None:
                window.dialog.done(0)
                window.dialog = None
            window.setDialog(c(program))
        except Exception as e:
            traceback.print_exc()

    return x


class LessonData:
    def __init__(self, lesson: Lesson, param):
        self.lesson = lesson
        self.param = param
        self.visit = len(self.lesson.visitations)
        self.total = len(students_of_groups(self.lesson.groups))

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


class QAnalysisDialog(QDialog):
    class DataType(int):
        WEEK = 1
        WEEK_DAY = 2

    # TODO destroy on exit (memory leak)
    def __init__(self, program: IProgram, parent=None):
        super().__init__(parent)
        self.program: IProgram = program
        # load data
        self.acc = LessonAccumulator(lessons=self.get_lessons())

        # load global statistic data
        # TODO make real global statistic load
        self.global_acc = LessonAccumulator()

        # initialise plots variables
        self._ax = None
        self._gp = None

        # parameters
        self.count = None

        try:
            self.figure = plt.figure()
            self.canvas = FigureCanvas(self.figure)

            self.info_label = QLabel()
            self.info_label.setFont(QFont('Sans', 22))

            # init plot type selector
            combobox_layout = QHBoxLayout()

            self.plot_type_label = QLabel('Тип графика')

            self.combo_box = QComboBox()
            self.combo_box.addItems("Ломаная,Гистограма,Диаграма размаха".split(','))
            self.combo_box.currentIndexChanged.connect(self.draw)

            combobox_layout.addWidget(self.plot_type_label)
            combobox_layout.addWidget(self.combo_box)

            layout = QVBoxLayout()
            layout.addWidget(self.info_label)
            layout.addWidget(self.canvas)

            layout.addLayout(combobox_layout)
            self.setLayout(layout)
        except Exception as e:
            print(e)

    def draw(self):
        # remove old and setup new
        self.ax().clear()
        self.format_ax()

        # depend on selected type
        if self.combo_box.currentIndex() == 0:
            self._plot()
        elif self.combo_box.currentIndex() == 1:
            self._hist()
        elif self.combo_box.currentIndex() == 2:
            self._boxplot()

        # refresh canvas
        self.canvas.draw()

    def ax(self):
        if self._ax is None:
            self._ax = self.figure.add_subplot(111)
        return self._ax

    def _plot(self):
        if self.global_acc.is_ready():
            self.ax().plot(self.acc.get_data(), label="Процент посещений ваших занятий")
            self.ax().plot(self.global_acc.get_data(), label="Процент посещений по университету")

            self.ax().legend()
        else:
            self.ax().plot(self.acc.get_data())

    def _hist(self):
        if self.global_acc.is_ready():
            self.ax().hist([self.acc.get_hist_data(), self.global_acc.get_hist_data()],
                           bins=range(0, self.count), align='right', rwidth=0.7, histtype='menu_bar',
                           label=["Процент посещений ваших занятий",
                                  "Процент посещений по университету"])

            self.ax().legend()
        else:
            N, bins, patches = self.ax().hist(self.acc.get_hist_data(),
                                              bins=range(0, self.count), align='right', rwidth=0.7)
            for i in range(len(patches)):
                if i % 2 == 0:
                    patches[i].set_facecolor(color="#ff8000")
                else:
                    patches[i].set_facecolor(color="#ff7010")

    def _boxplot(self):
        self.ax().boxplot(self.acc.get_box_data(), '*-', sym="")

    def get_lessons(self):
        raise NotImplementedError()
