from itertools import chain
from typing import List

from PyQt5.QtCore import pyqtSlot
from PyQt5.QtWidgets import QWidget, QMessageBox
from sqlalchemy import inspect

from Client.MyQt.Widgets.Network.SendNotifications import SendNotifications
from Client.MyQt.Widgets.Network.SendUpdate import SendUpdatesWidget
from Client.MyQt.Widgets.Table.Contacts import AdministrationModel
from Client.MyQt.Window.NotificationParam.UiDesign import Ui_NotificationWindow
from Client.MyQt.Window.interfaces import IDataBaseUser
from DataBase2 import Administration, Auth, Parent, Student, NotificationParam
from Domain.functools.Dict import format_view, validate_new_user
from Domain.interface import Singleton


class NotificationWindow(Singleton, QWidget, Ui_NotificationWindow, IDataBaseUser):
    class Tabs(int):
        NEW_USER = 0
        ADMIN_TABLE = 1
        PARENT_TABLE = 2

    def __init__(self, program, flags=None, *args, **kwargs):
        IDataBaseUser.__init__(self, program.session)
        QWidget.__init__(self, flags)
        Singleton.__init__(self)
        self.setupUi(self)

        self.program = program

        assert self.session == inspect(program.professor).session

        self.child_window = None

        self.professor = program.professor

        self.new_user_save_btn.clicked.connect(self.on_add_user)
        self.tabWidget.currentChanged.connect(self.on_change_tab)

        self.new_user_sex_combo_box.addItems(["Мужской", "Женский"])
        self.new_user_type_combo_box.addItems(["Студент", "Преподаватель", "Родитель", "Администрация университета"])
        self.new_user_type_combo_box.currentIndexChanged.connect(self.on_user_type_changed)
        self.new_user_type_combo_box.setCurrentIndex(2)

        self.student.setItems(Student.of(self.professor))

        self.save_btn.clicked.connect(self.save_action)

        self.notification_progress_window = None

        def run_notification():
            self.notification_progress_window = SendNotifications(
                host=self.program.host,
                professor=self.professor
            )
            self.notification_progress_window.show()

        self.run_btn.clicked.connect(run_notification)

    @pyqtSlot(name='save_action')
    def save_action(self):
        self.professor.session().commit()

        reply = QMessageBox().question(
            self,
            "Сохранено",
            "Данные успешно сохранены.\nХотите отправить изменения на сервер?",
            QMessageBox.Yes | QMessageBox.No
        )

        if reply == QMessageBox.Yes:
            SendUpdatesWidget(self.program).show()

        if self.tabWidget.currentIndex() == self.Tabs.ADMIN_TABLE:
            self.administration_table_view.setModel(AdministrationModel(NotificationParam.of(self.professor)))

    def on_add_user(self):
        if self.new_user_type_combo_box.currentIndex() == Auth.Type.ADMIN:
            admin_data = dict(last_name=self.new_user_last_name.text(),
                              first_name=self.new_user_first_name.text(),
                              middle_name=self.new_user_middle_name.text(),
                              email=self.new_user_email.text())

            if validate_new_user(admin_data):
                admin_data = format_view(admin_data)

                admin = Administration(**admin_data)
                np = NotificationParam()
                np.admin = admin
                np.professor = self.professor

                self.professor.session().add_all([admin, np])
                self.professor.session().commit()

                self.program.window.ok_message.emit('Контакт добавлен')
                self.tabWidget.setCurrentIndex(NotificationWindow.Tabs.ADMIN_TABLE)
            else:
                self.program.window.ok_message.emit(f'Необходимо заполнить поля [Фамилия, Имя, Отчество, Email]')
        elif self.new_user_type_combo_box.currentIndex() == Auth.Type.PARENT:

            raise NotImplementedError('TODO')

            self.tabWidget.setCurrentIndex(NotificationWindow.Tabs.PARENT_TABLE)

        for input_ in [self.new_user_email, self.new_user_middle_name,
                       self.new_user_first_name, self.new_user_last_name]:
            input_.clear()

    def on_change_tab(self, index):
        if index == NotificationWindow.Tabs.ADMIN_TABLE:
            self.show_admin_table()
        elif index == NotificationWindow.Tabs.PARENT_TABLE:
            self.show_parent_table()

    def show_admin_table(self):
        self.administration_table_view.setModel(AdministrationModel(NotificationParam.of(self.professor)))

    def show_parent_table(self):
        self.tableWidget_2.clear()

        students = Student.of(self.professor)
        lists_of_parents = map(lambda student: student.parents, students)
        parents: List[Parent] = chain.from_iterable(lists_of_parents)

        for parent in parents:
            self.tableWidget_2.add_row(parent)

    def on_user_type_changed(self, current_index):
        self.student_label.setHidden(current_index != Auth.Type.PARENT)
        self.student.setHidden(current_index != Auth.Type.PARENT)

    def showAsChild(self, *args):
        self.show()

    @pyqtSlot(name='on_sycnh_finished')
    def on_synch_finished(self):
        self.session.refresh(self.professor)

        if self.tabWidget.currentIndex() == NotificationWindow.Tabs.ADMIN_TABLE:
            self.show_admin_table()
        elif self.tabWidget.currentIndex() == NotificationWindow.Tabs.PARENT_TABLE:
            self.show_parent_table()
        else:
            pass
