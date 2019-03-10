from PyQt5.QtCore import QAbstractTableModel, QModelIndex, Qt, pyqtSignal
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QTableView, QLabel

from Client.MyQt.Widgets.Network.Request import RequestWidget
from Domain.Structures.DictWrapper.Network.Synch import ClientUpdateData, Changes
from Modules.Synch.ClientSide import Updater
from Parser import client_args


class UpdatesModel(QAbstractTableModel):
    def __init__(self, updates: Changes):
        super().__init__()

        self.updates = updates

    def columnCount(self, parent=None, *args, **kwargs):
        return 3

    def rowCount(self, parent=None, *args, **kwargs):
        return len(self.updates.created) + len(self.updates.updated) + len(self.updates.deleted)

    def get_value(self, index):
        created_len = len(self.updates.created)
        i = 0
        for key in self.updates.created.keys():
            for item in self.updates.created[key]:
                if i == index.row():
                    return item, 'created'
                i += 1
        updated_len = len(self.updates.updated)
        for key in self.updates.updated.keys():
            for item in self.updates.updated[key]:
                if i == index.row():
                    return item, 'updated'
                i += 1
        deleted_len = len(self.updates.deleted)
        for key in self.updates.deleted.keys():
            for item in self.updates.deleted[key]:
                if i == index.row():
                    return item, 'deleted'
                i += 1

    def data(self, index: QModelIndex, role=None):
        if role == Qt.DisplayRole:
            item, d = self.get_value(index)
            column = index.column()
            if column == 0:
                return type(item).__name__
            if column == 1:
                return item.id
            if column == 2:
                return d

    def headerData(self, p_int, orientation, role=None):
        if orientation == Qt.Horizontal:
            if role == Qt.DisplayRole:
                return ['Тип', 'ID', 'Статус'][p_int]


class SendUpdatesWidget(QWidget):
    start = pyqtSignal()
    def __init__(self, professor, flags=None, *args, **kwargs):
        super().__init__(flags, *args, **kwargs)
        self.setMinimumWidth(600)

        l = QVBoxLayout()

        updates = Changes(**professor.updates())

        if len(updates):
            def on_finish_update():
                self.table.setModel(UpdatesModel(Changes(**professor.updates())))

            widget = RequestWidget(
                professor=professor,
                worker=Updater(
                    professor,
                    ClientUpdateData(
                        updates=updates,
                        last_update_in=professor._last_update_in,
                        last_update_out=professor._last_update_out),
                    client_args.host
                ),
                text_button='Начать'
            )
            widget.setMinimumWidth(500)
            self.start.connect(widget.send)

            widget.finish.connect(on_finish_update)

            l.addWidget(widget)

            self.table = QTableView()
            self.table.setModel(UpdatesModel(updates))
            l.addWidget(self.table)

        else:
            l.addWidget(QLabel("Синхронизировано"))
            l.addWidget(QLabel(f'Последняя загрузка {str(professor._last_update_in)}'))
            l.addWidget(QLabel(f'Последняя выгрузка {str(professor._last_update_out)}'))

        self.setLayout(l)
