import sys

from PyQt5.QtChart import QChart, QBarSet, QBarSeries, QChartView, QBarCategoryAxis, QValueAxis
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QApplication, QMainWindow

from DataBase2 import Auth
from Domain.Aggregation import WeeksAggregation

if __name__ == '__main__':
    app = QApplication(sys.argv)

    w = QChart()

    series = QBarSeries()

    professor = Auth.log_in('VAE', '123456').user

    data = WeeksAggregation.by_professor(professor)

    for row in data.iterrows():
        print(row[1][0], row[1][1])
        bar_set = QBarSet(str(int(row[1][0])))
        value = int(row[1][1])
        bar_set.append(value)

        series.append(bar_set)

    w.addSeries(series)

    axis_y = QValueAxis()
    axis_y.setRange(0, 100)
    series.attachAxis(axis_y)
    w.addAxis(axis_y, Qt.AlignLeft)
    print(axis_y.setTickType(QValueAxis.TickFixed))

    axis_x = QBarCategoryAxis()
    axis_x.append([i for i in range(1, 19)])
    series.attachAxis(axis_x)
    w.addAxis(axis_x, Qt.AlignBottom)

    chart = QChartView(w)



    window = QMainWindow()
    window.setCentralWidget(chart)



    window.show()

    sys.exit(app.exec_())
