import datetime

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.ticker import FuncFormatter

from Main.DataBase.sql_handler import DataBaseWorker as sql
from Main.MyQt.Window.Chart.QAnalysisDialog import QAnalysisDialog, LessonData, LessonAccumulator
from Main.Types import WorkingData


class WeekDayChart(QAnalysisDialog):
    def __init__(self, parent=None):
        try:
            self.data_type = QAnalysisDialog.DataType.WEEK_DAY

            super().__init__(parent)

            self.draw()
        except Exception as e:
            print(e)

    def format_ax(self):
        self.ax().set_ylim(0, 100)
        self.ax().set_xlim(0, 7)

        self.ax().set_xticks(np.arange(7))
        if self.combo_box.currentIndex() > 0:
            self.ax().xaxis.set_major_formatter(
                FuncFormatter(lambda x, y: ['', 'Пн', 'Вт', "Ср", "Чт", "Пт", "Сб", "Вс"][x]))
        else:
            self.ax().xaxis.set_major_formatter(
                FuncFormatter(lambda x, y: ['Пн', 'Вт', "Ср", "Чт", "Пт", "Сб", "Вс"][x]))
        self.ax().set_yticks([i * 10 for i in range(10)])

        self.ax().set_xlabel("Дни недели")
        self.ax().set_ylabel("Процент посещений")

    def draw(self):
        self.ax().clear()
        self.format_ax()

        if self.combo_box.currentIndex() == 0:
            data = self.acc.get_data()
            self.ax().plot(data)
        elif self.combo_box.currentIndex() == 1:
            data = self.acc.get_hist_data()

            N, bins, patches = self.ax().hist(data, bins=range(0, len(data)), align='right', rwidth=0.7)
            for i in range(len(patches)):
                if i % 2 == 0:
                    patches[i].set_facecolor(color="#ff8000")
                else:
                    patches[i].set_facecolor(color="#ff7010")
        elif self.combo_box.currentIndex() == 2:
            data = self.acc.get_box_data()
            self.ax().boxplot(data, '*-', sym="")

        self.canvas.draw()

    def get_lessons(self):
        return [
            LessonData(
                i["id"],
                datetime.datetime.strptime(i["date"], '%d-%m-%Y %I:%M%p').weekday() - 1
            ) for i in sql.instance().get_lessons(professor_id=WorkingData.instance().professor["id"])
        ]
