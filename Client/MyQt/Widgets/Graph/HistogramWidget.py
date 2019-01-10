from collections import Counter

from Client.MyQt.Widgets.Graph.BarWidget import QBarGraphWidget


class Histogram(QBarGraphWidget):
    def __init__(self, data, flags, *args, **kwargs):
        counter = Counter(data)
        bars = list(range(min(counter.keys()), max(counter.keys())))
        heights = []
        for i in bars:
            if i in counter.keys():
                heights.append(counter[i])
            else:
                heights.append(0)

        super().__init__(bars, heights, flags, *args, **kwargs)

    def addPlot(self, data):
        counter = Counter(data)
        bars = list(range(min(counter.keys()), max(counter.keys())))
        heights = []
        for i in bars:
            if i in counter.keys():
                heights.append(counter[i])
            else:
                heights.append(0)

        super().addPlot({bars[i]: heights[i] for i in range(len(bars))})
