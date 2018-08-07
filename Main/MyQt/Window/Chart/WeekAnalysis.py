import datetime
import sys

import matplotlib.pyplot as plt
from PyQt5.QtWidgets import QApplication

import Main.config as config
from DataBase.sql_handler import DataBaseWorker as sql
from Main.MyQt.Window.Chart.QAnalysisDialog import QAnalysisDialog, LessonData


class WeekChart(QAnalysisDialog):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.count = 18
        self.global_acc.data = {1: [100, 43], 2: [100, 49], 3: [100, 57], 4: [100, 68], 5: [100, 67], 6: [100, 75],
                                7: [100, 64], 8: [100, 59], 9: [100, 58], 10: [100, 53], 11: [100, 56], 12: [0, 0],
                                13: [0, 0], 14: [0, 0], 15: [0, 0], 16: [0, 0], 17: [0, 0], 18: [0, 0]}

        self.draw()

    def format_ax(self):
        self.ax().set_ylim(0, 100)
        self.ax().set_xlim(0, self.count)

        self.ax().yaxis.grid(True)

        self.ax().set_xticks([i for i in range(self.count)])
        self.ax().set_yticks([i * 10 for i in range(10)])

        self.ax().set_xlabel("Недели")
        self.ax().set_ylabel("Процент посещений")

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
