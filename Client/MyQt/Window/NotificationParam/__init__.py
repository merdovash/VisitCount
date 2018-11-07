from itertools import chain
from typing import List

from PyQt5.QtWidgets import QDialog

from Client.IProgram import IProgram
from Client.MyQt.Window import IParentWindow
from Client.MyQt.Window.NotificationParam.UiDesign import Ui_NotificationWindow
from Client.MyQt.Window.interfaces import IChildWindow
from DataBase2 import Administration, Professor, UserType, Parent, Student
from Domain import Action, Prepare
from Domain.Action import NetAction


class NotificationWindow(QDialog, Ui_NotificationWindow, IParentWindow, IChildWindow):
    class Tabs(int):
        NEW_USER = 0
        ADMIN_TABLE = 1
        PARENT_TABLE = 2

    def __init__(self, professor: Professor, flags, *args, **kwargs):
        super(QDialog, self).__init__(flags, *args, **kwargs)
        super(IParentWindow, self).__init__()
        self.setupUi(self)

        self.professor = professor

        self.new_user_save_btn.clicked.connect(self.on_add_user)
        self.tabWidget.currentChanged.connect(self.on_change_tab)

        self.new_user_sex_combo_box.addItems(["Мужской", "Женский"])
        self.new_user_type_combo_box.addItems(["Студент", "Родитель", "Преподаватель", "Администрация университета"])
        self.new_user_type_combo_box.currentIndexChanged.connect(self.on_user_type_changed)
        self.new_user_type_combo_box.setCurrentIndex(2)

        self.student.setItems(Student.of(professor))

        self.tableWidget.set_professor(self.professor)

        program: IProgram = self.parent().program

        self.save_btn.clicked.connect(lambda: NetAction.send_updates(
            login=program.auth.login,
            password=program.auth.password,
            host=program.host,
            data=Prepare.updates(program.session),
            on_error=program.window.error.emit,
            on_finish=lambda: program.window.ok_message.emit('Успешно сохранено')
        ))

        self.run_btn.clicked.connect(lambda: NetAction.run_notification(
            login=program.auth.login,
            password=program.auth.password,
            host=program.host,
            on_finish=lambda: program.window.ok_message.emit('Успешно отправлено'),
            on_error=program.window.error.emit
        ))

    def on_add_user(self):
        if self.new_user_type_combo_box.currentIndex() == UserType.ADMIN:
            Action.create_administration(performer_id=self.professor.id,
                                         **dict(last_name=self.new_user_last_name.text(),
                                                first_name=self.new_user_first_name.text(),
                                                middle_name=self.new_user_middle_name.text(),
                                                email=self.new_user_email.text()))

            self.tabWidget.setCurrentIndex(NotificationWindow.Tabs.ADMIN_TABLE)
        elif self.new_user_type_combo_box.currentIndex() == UserType.PARENT:

            raise NotImplementedError('TODO')

            self.tabWidget.setCurrentIndex(NotificationWindow.Tabs.PARENT_TABLE)

        for input_ in [self.new_user_email, self.new_user_middle_name,
                       self.new_user_first_name, self.new_user_last_name]:
            input_.clear()

    def on_change_tab(self, index):
        print('hello')
        if index == NotificationWindow.Tabs.ADMIN_TABLE:
            self.show_admin_table()
        elif index == NotificationWindow.Tabs.PARENT_TABLE:
            self.show_parent_table()

    def show_admin_table(self):
        self.tableWidget.clear()

        admins: List[Administration] = Administration.of(self.professor)

        for admin in admins:
            assert admin is not None, f'admin is None, in list {admins}'
            self.tableWidget.add_row(admin)

    def show_parent_table(self):
        self.tableWidget_2.clear()

        students = Student.of(self.professor)
        lists_of_parents = map(lambda student: student.parents, students)
        parents: List[Parent] = chain.from_iterable(lists_of_parents)

        print(parents)

        for parent in parents:
            self.tableWidget_2.add_row(parent)

    def on_user_type_changed(self, current_index):
        self.student_label.setHidden(current_index != UserType.PARENT)
        self.student.setHidden(current_index != UserType.PARENT)

    def showAsChild(self, *args):
        self.exec_()
