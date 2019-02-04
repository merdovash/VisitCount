from typing import List, Dict, Callable

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QCheckBox, QFormLayout
from PyQtPlot.BarWidget import QBarGraphWidget

from DataBase2 import _DBObject
# from Main.DataBase.GlobalStatistic import Statistic
from Domain.Structures import Data


class PlotType:
    @staticmethod
    def WEEK(w: QBarGraphWidget):
        w.horizontal_ax.set_ticks(range(1, 19))
        w.vertical_ax.set_ticks(range(0, 110, 10))
        w.set_tooltip_func(lambda bar, value, name: f"{value}% посещений\n на {bar} неделе")
        w.horizontal_ax.set_label("Неделя")
        w.vertical_ax.set_label("Посещения, %")

    @staticmethod
    def WEEKDAY(w: QBarGraphWidget):
        w.horizontal_ax.set_ticks(range(1, 8))
        w.horizontal_ax.set_label('День недели')
        w.vertical_ax.set_ticks(range(0, 110, 10))
        w.vertical_ax.set_label("Посещения, %")
        w.set_tooltip_func(lambda bar, value, name:
                           f"{value}% посещений\n {'в пн.во вт.в ср.в чт.в пт.в сб.в вс'.split('.')[int(bar)]}")


class QAnalysisDialog(QWidget):
    """
    Базовый класс для отображения графиков
    """
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

    def __init__(self, data: Data, selector: Dict[str, List[_DBObject]], plot_styler: Callable[[QBarGraphWidget], None],
                 flags=None, *args, **kwargs):
        QWidget.__init__(self, flags, *args, **kwargs)

        self.data = data

        layout = QVBoxLayout()

        self.graph = QBarGraphWidget(
            bars=[],
            heights=[],
            name="1",
            flags=self
        )
        plot_styler(self.graph)

        layout.addWidget(self.graph, stretch=90)

        option_layout = QHBoxLayout()
        layout.addLayout(option_layout)

        self.option_map = {}
        for key in selector.keys():
            sub_option_layout = QVBoxLayout()
            option_layout.addLayout(sub_option_layout)

            sub_option_layout.addWidget(QLabel(key), alignment=Qt.AlignCenter)

            items_layout = QFormLayout()
            sub_option_layout.addLayout(items_layout)
            for item in selector[key]:
                check_box = QCheckBox()
                check_box.setChecked(True)
                self.option_map[check_box] = item
                check_box.stateChanged.connect(self.draw)
                items_layout.addRow(str(item), check_box)

        self.setLayout(layout)

        self.draw()

    def draw(self):
        ignored = [self.option_map[key] for key in self.option_map.keys() if not key.isChecked()]
        data = self.data.avg(ignored=ignored)
        bars = sorted(data.keys())
        heights = [int(data[key] * 100) for key in bars]

        self.graph.update_data({bars[i]: heights[i] for i in range(len(bars))}, name='1')
