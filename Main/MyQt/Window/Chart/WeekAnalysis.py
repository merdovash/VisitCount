import datetime
import sys

import matplotlib.pyplot as plt
import numpy as np
from PyQt5.QtWidgets import QApplication

import Main.config as config
from Main.DataBase.sql_handler import DataBaseWorker as sql
from Main.MyQt.Window.Chart.QAnalysisDialog import QAnalysisDialog, LessonData, LessonAccumulator


class WeekChart(QAnalysisDialog):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.draw()

    def format_ax(self):
        self.ax().set_ylim(0, 100)
        #self.ax().set_xlim(0, len(data))

        self.ax().yaxis.grid(True)

        #self.ax().set_xticks([i for i in range(len(data))])
        self.ax().set_yticks([i * 10 for i in range(10)])

        self.ax().set_xlabel("Недели")
        self.ax().set_ylabel("Процент посещений")

    def draw(self):
        self.ax().clear()
        self.format_ax()

        if self.combo_box.currentIndex() == 0:
            data = self.acc.get_data()
            self.ax().plot(data, '*-')
        elif self.combo_box.currentIndex() == 1:
            data = self.acc.get_hist_data()
            N, bins, patches = self.ax().hist(data, bins=range(0, 18), align='right', rwidth=0.7)
            self.ax().set_xticks([i for i in range(18)])
            for i in range(len(patches)):
                if i % 2 == 0:
                    patches[i].set_facecolor(color="#ff8000")
                else:
                    patches[i].set_facecolor(color="#ff7010")
        elif self.combo_box.currentIndex() == 2:
            data = self.acc.get_box_data()
            self.ax().boxplot(data, '*-', sym="")

        # refresh canvas
        self.canvas.draw()

    def get_lessons(self):
        lessons = [
            LessonData(
                i[0],
                datetime.datetime.strptime(i[1], '%d-%m-%Y %I:%M%p').isocalendar()[1]
            ) for i in sql.instance().sql_request("SELECT id, {0}.date from {0}", config.lessons)
        ]

        lessons.sort(key=lambda x: x.param)
        start = lessons[0].param - 1

        for lesson in lessons:
            lesson.param -= start

        return lessons


if __name__ == "__main__":
    print(plt.style.available)
    app = QApplication(sys.argv)

    main = WeekChart()
    main.show()

    sys.exit(app.exec_())
