from operator import xor

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QTableWidget, QTableWidgetItem, QComboBox

from DataBase2 import Administration, Parent
from Domain.Data import student_info, find


class Header(int):
    LAST_NAME = 0
    FIRST_NAME = 1
    MIDDLE_NAME = 2
    EMAIL = 3

    STATUS = 4
    STUDENT = 4

    COUNT = 5


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
            print("notification status changed")
            print()
            self.value.data = bool(self.currentIndex())


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

        self.resizeColumnsToContents()

    def clear(self):
        for i in range(self.rowCount()):
            self.removeRow(0)

    def on_item_change(self, item: ContactTableItem):
        if isinstance(item, ContactTableComboItem):
            item.on_update()
