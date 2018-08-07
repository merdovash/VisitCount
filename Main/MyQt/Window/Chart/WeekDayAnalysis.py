import datetime
import traceback

import numpy as np
from matplotlib.ticker import FuncFormatter

from DataBase.sql_handler import DataBaseWorker as sql
from Main.MyQt.Window.Chart.QAnalysisDialog import QAnalysisDialog, LessonData
from Main.Types import WorkingData


class WeekDayChart(QAnalysisDialog):
    def __init__(self, parent=None):
        try:
            self.data_type = QAnalysisDialog.DataType.WEEK_DAY
            super().__init__(parent)

            self.global_acc.data = {0: [100, 63], 1: [100, 64], 2: [100, 67], 3: [100, 60], 4: [100, 53], 5: [100, 44]}
            self.count = 7

            self.draw()
        except Exception as e:
            print(e)
            traceback.print_exc()

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

    def get_lessons(self):
        return [
            LessonData(
                i["id"],
                datetime.datetime.strptime(i["date"], '%d-%m-%Y %I:%M%p').weekday() - 1
            ) for i in sql.instance().get_lessons(professor_id=WorkingData.instance().professor["id"])
        ]
