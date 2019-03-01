from __future__ import unicode_literals
import sys
import os
import random
import matplotlib
# Make sure that we are using QT5
from PyQt5.QtWidgets import QSizePolicy, QApplication

from DataBase2 import Student, Professor, Faculty, Discipline, Group
from Domain.Plot.plot import plot

matplotlib.use('Qt5Agg')
# Uncomment this line before running, it breaks sphinx-gallery builds
# from PyQt5 import QtCore, QtWidgets

from numpy import arange, sin, pi
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure

progname = os.path.basename(sys.argv[0])
progversion = "0.1"


class MyMplCanvas(FigureCanvas):
    """Ultimately, this is a QWidget (as well as a FigureCanvasAgg, etc.)."""

    def __init__(self, student, group_by, plot_type, semester, parent=None, width=5, height=4, dpi=100):
        fig = Figure(figsize=(width, height), dpi=dpi, )

        self.axes = fig.add_axes([0.05, 0.15, 0.7, 0.8])

        self.user = student
        self.group_by = group_by
        self.plot_type = plot_type
        self.semester = semester

        self.compute_initial_figure()

        FigureCanvas.__init__(self, fig)
        self.setParent(parent)

        FigureCanvas.setSizePolicy(self,
                                   QSizePolicy.Expanding,
                                   QSizePolicy.Expanding)
        FigureCanvas.updateGeometry(self)

    def compute_initial_figure(self):
        plot(
            self.user,
            self.axes,
            group_by=self.group_by,
            plot_type=self.plot_type,
            semester=self.semester
        )
        self.axes.tick_params(axis='x', rotation=30)
        self.axes.legend(bbox_to_anchor=(1, 1))
        self.axes.grid(True)
        # self.axes.subplots_adjust(left=0.04, right=0.7, top=0.9, bottom=0.1)


if __name__ == '__main__':
    app = QApplication(sys.argv)

    w = MyMplCanvas(Professor.get(id=1), lambda x: Group.of(x))

    w.show()

    sys.exit(app.exec_())
