from PyQt5.QtCore import QAbstractTableModel, QModelIndex, Qt
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QTableView

from Client.MyQt.Widgets.Network.Request import RequestWidget
from Domain.Structures.DictWrapper.Network.Synch import ClientUpdateData, Updates
from Modules.Synch.ClientSide import ApplyUpdate


class UpdatesModel(QAbstractTableModel):
    def __init__(self, updates: Updates):
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
    def __init__(self, program, flags=None, *args, **kwargs):
        super().__init__(flags, *args, **kwargs)
        from Modules.Synch import address

        professor = program.professor

        l = QVBoxLayout()

        updates = Updates(**professor.updates())

        widget = RequestWidget(
            professor=professor,
            data=ClientUpdateData(
                updates=updates,
                last_update_in=professor._last_update_in,
                last_update_out=professor._last_update_out),
            address=program.host + address,
            title='Отправить обновления на сервер',
            text_button='Начать',
            on_response=ApplyUpdate(program.professor),
            on_error=lambda x: None,
            on_finish=lambda x: None
        )
        widget.setMinimumWidth(500)
        widget.on_finish = self.close

        l.addWidget(widget)

        self.table = QTableView()
        self.table.setModel(UpdatesModel(updates))

        l.addWidget(self.table)

        self.setLayout(l)
