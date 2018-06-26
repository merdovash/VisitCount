from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel

from Main import config


class QDownloadLabel(QLabel):
    class Status(int):
        Ready = "✅"
        Steady = "⏸"

    def __init__(self, header):
        super().__init__()
        self.header = header
        self.status = QDownloadLabel.Status.Steady
        self.total = ""
        self.setProgress(0)

    def setTotal(self, v):
        self.total = v
        self.setProgress(0)

    def setProgress(self, a0):
        self.setText(self.status+" {0}: {1} / {2}".format(self.header, a0, self.total))

    def setReady(self):
        self.status = QDownloadLabel.Status.Ready
        self.setProgress(self.total)


class QLoadingWidget(QWidget):
    def __init__(self):
        super().__init__()

        self.l = QVBoxLayout()
        self.tables = [config.students,
                       config.groups,
                       config.students_groups,
                       config.disciplines,
                       config.lessons,
                       config.professors,
                       config.visitation]

        self.labels = [QDownloadLabel(i) for i in self.tables]

        for l in self.labels:
            self.l.addWidget(l)

        self.current_table = None

        self.setLayout(self.l)

    def setTotals(self, data):
        for key in data:
            self.labels[self.tables.index(key)].setTotal(len(data[key]))

    def setMarker(self, marker):
        if marker["table"] in self.tables:
            if self.current_table is None:
                self.current_table = marker["table"]
            else:
                if marker["table"] != self.current_table:
                    self.labels[self.tables.index(self.current_table)].setReady()
                    self.current_table = marker["table"]
            index = self.tables.index(marker["table"])
            self.labels[index].setProgress(marker["inserted"])
