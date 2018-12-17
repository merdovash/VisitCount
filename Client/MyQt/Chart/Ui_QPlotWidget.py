import matplotlib.pyplot as plt
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QFormLayout, QCheckBox, QComboBox, QHBoxLayout, QLabel, QVBoxLayout
from matplotlib.backends.backend_qt5agg import \
    FigureCanvasQTAgg as FigureCanvas, \
    NavigationToolbar2QT as NavigationToolbar
from matplotlib.figure import Figure

from Client.MyQt.Widgets.HLine import HLine
from DataBase2 import Group, Discipline
from Domain.Data import names_of_groups


class Ui_PlotWidget:
    def setupUi(self, QPlotWidget, css=""):
        QPlotWidget.setWindowFlags(QPlotWidget.windowFlags())

        QPlotWidget.setMinimumWidth(600)
        QPlotWidget.setMinimumHeight(600)

        self.figure = plt.figure()
        self.canvas = FigureCanvas(Figure(figsize=(5, 3)))

        self._ax = self.canvas.figure.subplots()

        self.toolbar = NavigationToolbar(self.canvas, self)

        # init plot type selector
        combobox_layout = QHBoxLayout()

        self.plot_type_label = QLabel('Тип графика')

        self.combo_box = QComboBox()
        self.combo_box.setStyleSheet(css)
        self.combo_box.addItems("Столбчатая диаграмма,Ломаная".split(','))
        self.combo_box.currentIndexChanged.connect(QPlotWidget.draw)

        combobox_layout.addWidget(self.plot_type_label)
        combobox_layout.addWidget(self.combo_box)

        layout = QVBoxLayout()
        layout.addWidget(self.canvas, 1)
        layout.addWidget(self.toolbar, 1)

        layout.addLayout(combobox_layout)

        layout.addWidget(HLine())

        self.__init_control_panel__(QPlotWidget, layout)

        self.setLayout(layout)

    def __init_control_panel__(self, QPlotWidget, layout):
        QPlotWidget.groups = {}
        QPlotWidget.disciplines = {}

        params_layout = QHBoxLayout()
        layout.addLayout(params_layout)

        group_layout = QFormLayout()
        for group in Group.of(QPlotWidget.professor, flat_list=True):
            def action(g):
                def a():
                    QPlotWidget.groups[g] = not QPlotWidget.groups[g]
                    QPlotWidget.refresh_data()
                    QPlotWidget.draw()

                return a

            check_box = QCheckBox()
            QPlotWidget.groups[group] = True
            check_box.setCheckState(Qt.Checked)
            check_box.stateChanged.connect(action(group))
            group_layout.addRow(names_of_groups(group), check_box)

        params_layout.addLayout(group_layout)

        discipline_layout = QFormLayout()
        for disc in Discipline.of(QPlotWidget.professor):
            def action(d):
                def a():
                    QPlotWidget.disciplines[d] = not QPlotWidget.disciplines[d]
                    QPlotWidget.refresh_data()
                    QPlotWidget.draw()

                return a

            check_box = QCheckBox()
            QPlotWidget.disciplines[disc] = True
            check_box.setCheckState(Qt.Checked)
            check_box.stateChanged.connect(action(disc))
            discipline_layout.addRow(disc.name, check_box)

        params_layout.addLayout(discipline_layout)
