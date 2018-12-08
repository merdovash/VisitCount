from PyQt5.QtWidgets import QWidget
from matplotlib.axes import Axes

from Client.IProgram import IProgram
from Client.MyQt.Chart.Ui_QPlotWidget import Ui_PlotWidget
from Client.MyQt.Window.interfaces import IParentWindow, IChildWindow
from Domain.Aggregation import Column


# from Main.DataBase.GlobalStatistic import Statistic


def show(graph_window_constructor, program: IProgram):
    def x():
        window = program.window
        if isinstance(window, IParentWindow):
            dialog = graph_window_constructor(program)
            dialog.setStyleSheet(program.css)
            window.setDialog(graph_window_constructor(program))
        else:
            raise TypeError(f'window {window} is not able to take child window')

    return x


class QAnalysisDialog(QWidget, IParentWindow, IChildWindow, Ui_PlotWidget):
    instances = {}

    @staticmethod
    def instance(type_, **kwargs) -> 'QAnalysisDialog':
        if QAnalysisDialog.instances.get(type_, None) is None:
            QAnalysisDialog.instances[type_] = type_(**kwargs)
        return QAnalysisDialog.instances[type_]

    @staticmethod
    def loader(type_, **kwargs):
        def f():
            inst = QAnalysisDialog.instance(type_, **kwargs)
            inst.show()

        return f

    class DataType(int):
        WEEK = 1
        WEEK_DAY = 2

    plot_types = {
        0: dict(type='bar', xlabel=None, ylabel='Процент посещений'),
        1: dict(type='hist', xlabel='Процент посещений', ylabel='Количество занятий'),
    }

    # TODO destroy on exit (memory leak)
    def __init__(self, program: IProgram, parent=None):
        QWidget.__init__(self, parent)
        IParentWindow.__init__(self)
        IChildWindow.__init__(self)

        self.setStyleSheet(program.css)
        self.program: IProgram = program
        self.professor = program.professor

        # initialise plots variables
        self._ax = None
        self._gp = None

        # parameters
        self.count = None

        Ui_PlotWidget.setupUi(self, self, program.css)

    def refresh_data(self):
        raise NotImplementedError()

    def draw(self):
        # remove old and setup new
        self.ax().clear()

        index = self.combo_box.currentIndex()

        plot_legend = self.plot_types[index]

        kwargs = {'ylim': [0, 100] if index == 0 else None}
        try:
            try:
                self._draw(ax=self.ax(), plot_type=plot_legend['type'], color='#ff8000', **kwargs)
            except TypeError:
                self.ax().plot(x=0, y=0)
        except TypeError:
            self.program.window.error.emit('Пусто')

        if plot_legend['xlabel'] is not None:
            self.ax().set_xlabel(plot_legend['xlabel'])
        if plot_legend['ylabel'] is not None:
            self.ax().set_ylabel(plot_legend['ylabel'])

        # refresh canvas
        self.canvas.draw()

    def ax(self) -> Axes:
        return self._ax

    def _draw(self, plot_type, ax, **kwargs):
        self.get_data().plot(
            x=Column.date,
            y=Column.visit_rate,
            ax=ax,
            kind=plot_type,
            title='Посещения',
            **kwargs)

    def showAsChild(self, *args):
        self.show()

    def closeEvent(self, QCloseEvent):
        self.setVisible(False)
