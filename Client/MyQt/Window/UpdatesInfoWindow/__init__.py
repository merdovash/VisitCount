from PyQt5.QtGui import QCloseEvent
from PyQt5.QtWidgets import QWidget, QTabWidget, QListWidget, QVBoxLayout

from Client.MyQt.Widgets.QEasyTable import QEasyTable


class UpdatesInfoWidget(QWidget):
    def __init__(self, updates, flags=None, *args, **kwargs):
        QWidget.__init__(self, flags, *args, **kwargs)
        layout = QVBoxLayout()

        self.setWindowTitle('Информация об обновлениях (отправка)')

        self.table = QEasyTable(header=[
            dict(name='table',
                 value='Таблица'),
            dict(name='id',
                 value='Строка'),
            dict(name='type',
                 value='Тип обновления'),
            dict(name='date',
                 value='Дата')
        ])

        layout.addWidget(self.table)

        self.setLayout(layout)

        self.tabs = QTabWidget()
        for case in updates:
            list_widget = QListWidget()
            list_widget.addItems(updates[case])

            self.tabs.addTab(list_widget, case)

        self.layout_ = QVBoxLayout()
        self.layout_.addWidget(self.tabs)
        self.setLayout(self.layout_)
