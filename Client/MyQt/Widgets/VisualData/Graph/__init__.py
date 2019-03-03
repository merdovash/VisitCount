from __future__ import unicode_literals

import os
import sys

import matplotlib
# Make sure that we are using QT5
from PyQt5.QtWidgets import QSizePolicy, QApplication

from DataBase2 import Professor, Group
from Domain.Plot.plot import plot

matplotlib.use('Qt5Agg')
# Uncomment this line before running, it breaks sphinx-gallery builds
# from PyQt5 import QtCore, QtWidgets

from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure


class MyMplCanvas(FigureCanvas):
    """Ultimately, this is a QWidget (as well as a FigureCanvasAgg, etc.)."""

    def __init__(self, student, group_by, plot_type, semester, parent=None):
        self.user = student
        self.group_by = group_by
        self.plot_type = plot_type
        self.semester = semester

        fig = self.compute_initial_figure()

        FigureCanvas.__init__(self, fig)
        self.setParent(parent)

        FigureCanvas.setSizePolicy(self,
                                   QSizePolicy.Expanding,
                                   QSizePolicy.Expanding)
        FigureCanvas.updateGeometry(self)

    def compute_initial_figure(self):
        fig = plot(
            self.user,
            group_by=self.group_by,
            plot_type=self.plot_type,
            semester=self.semester
        )

        return fig
        # self.axes.subplots_adjust(left=0.04, right=0.7, top=0.9, bottom=0.1)


if __name__ == '__main__':
    app = QApplication(sys.argv)

    w = MyMplCanvas(Professor.get(id=1), lambda x: Group.of(x))

    w.showFullScreen()

    sys.exit(app.exec_())
