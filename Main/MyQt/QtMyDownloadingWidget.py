from PyQt5.QtWidgets import QWidget, QLabel, QProgressBar, QFormLayout

from Main import config


class QLoadingWidget(QWidget):
    def __init__(self):
        super().__init__()

        self.inner_layout = QFormLayout()
        self.tables = [config.students,
                       config.groups,
                       config.students_groups,
                       config.disciplines,
                       config.lessons,
                       config.professors,
                       config.visitation,
                       config.auth]

        self.labels = [[QLabel(i), QProgressBar()] for i in self.tables]

        for i in self.labels:
            self.inner_layout.addRow(i[0], i[1])

        self.setLayout(self.inner_layout)
        self.current_table = None

    def update(self, l):
        if l.table in self.tables:
            if self.current_table is None:
                self.current_table = l.table
            if self.current_table != l.table:
                self.labels[self.tables.index(self.current_table)][1].setValue(100)
                self.current_table = l.table
            else:
                self.labels[self.tables.index(l.table)][1].setValue(l.inserted / l.total*100)
