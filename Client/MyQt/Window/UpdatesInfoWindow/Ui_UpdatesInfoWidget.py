from PyQt5.QtWidgets import QVBoxLayout
from PyQt5.QtWidgets import QWidget

from Client.MyQt.Widgets.QEasyTable import QEasyTable


class Ui_UpdatesInfoWidget:
    def setupUi(self, UpdatesInfoWidget: QWidget):
        layout = QVBoxLayout()

        UpdatesInfoWidget.setWindowTitle('Информация об обновлениях (отправка)')

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

        UpdatesInfoWidget.setLayout(layout)
