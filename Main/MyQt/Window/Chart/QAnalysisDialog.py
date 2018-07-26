import traceback
from abc import abstractmethod

import numpy as np
from math import ceil

import sys
from PyQt5.QtWidgets import QDialog, QVBoxLayout, QComboBox
import matplotlib.pyplot as plt

from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas

# from Main.DataBase.GlobalStatistic import Statistic
from Main.MyQt.Window.Chart.Tools import get_visit_count, get_student_count


def show(c, parent):
    def x():
        try:
            if parent.dialog is not None:
                parent.dialog.done(0)
                parent.dialog = None
            parent.setDialog(c())
        except Exception as e:
            traceback.print_exc()

    return x


class LessonData:
    def __init__(self, lesson_id, param):
        self.id = lesson_id
        self.param = param
        self.visit = get_visit_count(self.id)
        self.total = get_student_count(self.id)

    def __repr__(self):
        return "(id: {}, param: {}, visit: {}/{})".format(self.id, self.param, self.visit, self.total)


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


class QAnalysisDialog(QDialog):
    class DataType(int):
        WEEK = 1
        WEEK_DAY = 2

    # TODO destroy on exit (memory leak)
    def __init__(self, parent=None):
        super().__init__(parent)

        self.acc = LessonAccumulator(lessons=self.get_lessons())
        # self.global_acc = Statistic(self.data_type)
        self._ax = None
        try:
            self.figure = plt.figure()

            self.canvas = FigureCanvas(self.figure)

            # self.toolbar = NavigationToolbar(self.canvas, self)

            self.combo_box = QComboBox()
            self.combo_box.addItems("Ломаная,Гистограма,Диаграма размаха".split(','))
            self.combo_box.currentIndexChanged.connect(self.draw)
            layout = QVBoxLayout()
            # layout.addWidget(self.toolbar)
            layout.addWidget(self.canvas)
            layout.addWidget(self.combo_box)
            self.setLayout(layout)
        except Exception as e:
            print(e)

    def ax(self):
        if self._ax is None:
            self._ax = self.figure.add_subplot(111)
        return self._ax

    @abstractmethod
    def get_lessons(self):
        pass
