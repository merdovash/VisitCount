import sys
from operator import xor
from typing import List

from PyQt5.QtCore import Qt, QAbstractTableModel, QModelIndex, QVariant
from PyQt5.QtGui import QColor
from PyQt5.QtWidgets import QTableWidget, QTableWidgetItem, QComboBox, QTableView, QApplication, QHeaderView

from Client.MyQt.Widgets.Buttons import DeleteContactButton
from DataBase2 import Administration, Parent, NotificationParam, Auth
from Domain.Data import student_info
from Domain.functools.List import find


class Header(int):
    LAST_NAME = 0
    FIRST_NAME = 1
    MIDDLE_NAME = 2
    EMAIL = 3

    STATUS = 4
    STUDENT = 4

    DELETE = 5

    COUNT = 6


class UpdateableItem:
    def __init__(self, item, user, professor):
        self.user = user
        self.professor = professor
        self.item = item

    @property
    def data(self):
        raise NotImplementedError()

    @data.setter
    def data(self, value):
        raise NotImplementedError()


class BlockedUpdateItem(UpdateableItem):
    def __init__(self, item: QTableWidgetItem, user, professor):
        super().__init__(item, user, professor)
        item.setFlags(xor(item.flags(), Qt.ItemIsEditable))
        self.text = item.text()

    @property
    def data(self):
        raise NotImplementedError()

    @data.setter
    def data(self, value):
        self.item.setText(self.text)


class FirstNameItem(BlockedUpdateItem):
    @property
    def data(self):
        return self.user.first_name


class LastNameItem(BlockedUpdateItem):
    @property
    def data(self):
        return self.user.last_name


class MiddleNameItem(BlockedUpdateItem):
    @property
    def data(self):
        return self.user.first_name


class EmailItem(UpdateableItem):
    @property
    def data(self):
        return self.user.email

    @data.setter
    def data(self, value):
        self.user.email = value


class ActiveStatusItem(UpdateableItem):
    @property
    def data(self):
        return self.user.active

    @data.setter
    def data(self, value):
        self.user.active = value


class StudentInfoItem(BlockedUpdateItem):
    @property
    def data(self):
        return student_info(self.user.students)

    @data.setter
    def data(self, value):
        super().data = value


class ContactTableItem(QTableWidgetItem):
    def __init__(self, user, professor, Type):
        super(QTableWidgetItem, self).__init__()

        self.value = Type(self, user, professor)
        # super(Type).__init__(user, professor)

        self.setText(str(self.value.data))

    def on_update(self):
        try:
            self.value.data = self.text()
        except AttributeError:
            pass


class ContactTableComboItem(QComboBox):
    def __init__(self, user, professor, Type):
        super().__init__()

        self.value = Type(self, user, professor)

        self.addItems(["Оповещение выключено", "Оповещение включено"])
        self.setCurrentIndex(int(self.value.data))

        self.currentIndexChanged.connect(self.on_update)

    def on_update(self, *args):
        if int(self.value.data) != self.currentIndex():
            self.value.data = bool(self.currentIndex())


class AdministrationModel(QAbstractTableModel):
    def __init__(self, notification_params):
        super().__init__()
        self.params: List[NotificationParam] = notification_params
        self.calc_map()

        self.updated = {}

    def calc_map(self):
        self.map = [
            [
                param.admin.last_name,
                param.admin.first_name,
                param.admin.middle_name,
                param.admin.email,
                Qt.Checked if param.active else Qt.Unchecked,
                Qt.Checked if param.show_groups else Qt.Unchecked,
                Qt.Checked if param.show_disciplines else Qt.Unchecked,
                Qt.Checked if param.show_students else Qt.Unchecked
            ]
            for param in self.params]

    def setData(self, index:QModelIndex, value, role=None):
        if index.column() in range(3,8):
            if role == Qt.CheckStateRole:
                self.set_value(index, not self.get_value(index))
                return True
        return False

    def set_value(self, index, value):
        if index not in self.updated.keys():
            self.updated[index] = self.get_value(index)
        if value == self.updated[index]:
            del self.updated[index]

        np = self.params[index.row()]
        if index.column() == 0:
            np.admin.last_name = value
        if index.column() == 1:
            np.admin.first_name = value
        if index.column() == 2:
            np.admin.middle_name = value
        if index.column() == 3:
            np.admin.email = value
        if index.column() == 4:
            np.active = value
        if index.column() == 5:
            np.show_groups = value
        if index.column() == 6:
            np.show_disciplines = value
        if index.column() == 7:
            np.show_students = value

    def get_value(self, index):
        np = self.params[index.row()]
        if index.column() == 0:
            return np.admin.last_name
        if index.column() == 1:
            return np.admin.first_name
        if index.column() == 2:
            return np.admin.middle_name
        if index.column() == 3:
            return np.admin.email
        if index.column() == 4:
            return np.active
        if index.column() == 5:
            return np.show_groups
        if index.column() == 6:
            return np.show_disciplines
        if index.column() == 7:
            return np.show_students

    def data(self, index: QModelIndex, role=None):
        if index.column() in range(4, 8):
            if role == Qt.CheckStateRole:
                return Qt.Checked if self.get_value(index) else Qt.Unchecked
        if index.column() in range(0, 4):
            if role == Qt.DisplayRole:
                return self.get_value(index)
        if role == Qt.BackgroundColorRole:
            if index in self.updated.keys():
                return QColor(200, 200, 0, 100)

        if role == Qt.ToolTipRole:
            if index in self.updated.keys():
                return f'Поле было изменено\nЗначение до изменения: {self.updated[index]}'
        return QVariant()

    def flags(self, index: QModelIndex):
        if index.column() in range(3,8):
            return Qt.ItemIsUserCheckable | Qt.ItemIsEnabled
        return Qt.ItemIsEnabled

    def rowCount(self, parent=None, *args, **kwargs):
        return len(self.params)

    def columnCount(self, parent=None, *args, **kwargs):
        if len(self.map):
            return len(self.map[0])
        else:
            return 0

    def headerData(self, p_int, orientation, role=None):
        if role == Qt.DisplayRole:
            if orientation == Qt.Horizontal:
                return [
                    "Фамилия",
                    "Имя",
                    "Отчество",
                    "email",
                    "Статус",
                    "Отправлять\nгруппировку по\nгруппам",
                    "Отправлять\nгруппировку по\nдисциплинам",
                    "Отправлять\nгруппировку по\nстудентам",
                    "Удалить"
                ][p_int]
            else:
                return str(p_int + 1)


class QAdministrationTable(QTableView):
    LAST_NAME = 0
    FIRST_NAME = 1
    MIDDLE_NAME = 2
    EMAIL = 3
    STATUS = 4
    SHOW_GROUPS = 5
    SHOW_DISCIPLINES = 6
    SHOW_STUDENTS = 7

    DELETE = 8

    def __init__(self, *__args):
        super().__init__(*__args)
        self.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)

    def add_row(self, admin: Administration):
        row = self.rowCount()
        self.setRowCount(row + 1)

        self.setItem(row, self.LAST_NAME, QTableWidgetItem(admin.last_name))


class ContactTable(QTableWidget):

    def __init__(self, Class, *__args):
        super().__init__(*__args)

        self.professor = None

        self.Class = Class

        self.setColumnCount(Header.COUNT)

        self.setHorizontalHeaderItem(Header.LAST_NAME, QTableWidgetItem("Фамилия"))
        self.setHorizontalHeaderItem(Header.FIRST_NAME, QTableWidgetItem("Имя"))
        self.setHorizontalHeaderItem(Header.MIDDLE_NAME, QTableWidgetItem("Отчество"))
        self.setHorizontalHeaderItem(Header.EMAIL, QTableWidgetItem("email"))
        if Class == Administration:
            self.setHorizontalHeaderItem(Header.STATUS, QTableWidgetItem("Статус"))
        elif Class == Parent:
            self.setHorizontalHeaderItem(Header.STUDENT, QTableWidgetItem("Студент"))
        self.setHorizontalHeaderItem(Header.DELETE, QTableWidgetItem('Удалить'))

        self.itemChanged.connect(self.on_item_change)

    def set_professor(self, professor):
        self.professor = professor

    def add_row(self, user, index=None):
        if index is None:
            index = self.rowCount()

        self.insertRow(index)

        self.setItem(
            index,
            Header.LAST_NAME,
            ContactTableItem(user, self.professor, LastNameItem))
        self.setItem(
            index,
            Header.FIRST_NAME,
            ContactTableItem(user, self.professor, FirstNameItem))
        self.setItem(
            index,
            Header.MIDDLE_NAME,
            ContactTableItem(user, self.professor, MiddleNameItem))
        self.setItem(
            index,
            Header.EMAIL,
            ContactTableItem(user, self.professor, EmailItem))
        if isinstance(user, Administration):
            self.setCellWidget(
                index,
                Header.STATUS,
                ContactTableComboItem(find(lambda note: note.professor_id == self.professor.id,
                                           user.notification),
                                      self.professor,
                                      ActiveStatusItem))
        elif self.Class == Parent:
            self.setItem(
                index,
                Header.STATUS,
                ContactTableItem(user, self.professor, StudentInfoItem))

        self.setCellWidget(index, Header.DELETE, DeleteContactButton(user, self, index))

        self.resizeColumnsToContents()

    def clear(self):
        for i in range(self.rowCount()):
            self.removeRow(0)

    def on_item_change(self, item: ContactTableItem):
        if isinstance(item, ContactTableComboItem):
            item.on_update()


if __name__ == '__main__':
    app = QApplication(sys.argv)

    w = QAdministrationTable()
    auth = Auth.log_in('VAE', '123456')

    w.setModel(AdministrationModel(NotificationParam.of(auth.user)))
    w.show()

    sys.exit(app.exec_())
