from typing import List

from PyQt5.QtWidgets import QDialog

from Client.MyQt.Window.NotificationParam.UiDesign import Ui_NotificationWindow
from DataBase2 import Administration, Professor, UserType, Parent


class NotificationWindow(QDialog, Ui_NotificationWindow):
    class Tabs(int):
        NEW_USER = 0
        ADMIN_TABLE = 1
        PARENT_TABLE = 2

    def __init__(self, professor: Professor, flags, *args, **kwargs):
        super().__init__(flags, *args, **kwargs)

        self.setupUi(self)

        self.professor = professor

        self.new_user_save_btn.clicked.connect(self.on_add_user)
        self.tabWidget.currentChanged.connect(self.on_change_tab)

        self.new_user_sex_combo_box.addItems(["Мужской", "Женский"])
        self.new_user_type_combo_box.addItems(["Студент", "Родитель", "Преподаватель", "Администрация университета"])
        self.new_user_type_combo_box.currentIndexChanged.connect(self.on_user_type_changed)
        self.new_user_type_combo_box.setCurrentIndex(2)

        self.student.setItems(professor.students)

        self.tableWidget.set_professor(self.professor)

    def on_add_user(self):
        if self.new_user_type_combo_box.currentIndex() == UserType.ADMIN:
            admin = Administration.new(last_name=self.new_user_last_name.text(),
                                       first_name=self.new_user_first_name.text(),
                                       middle_name=self.new_user_middle_name.text(),
                                       email=self.new_user_email.text(),
                                       professor=self.professor)

            self.tabWidget.setCurrentIndex(NotificationWindow.Tabs.ADMIN_TABLE)
        elif self.new_user_type_combo_box.currentIndex() == UserType.PARENT:

            parent = Parent.new(first_name=self.new_user_first_name.text(),
                                last_name=self.new_user_last_name.text(),
                                middle_name=self.new_user_middle_name.text(),
                                email=self.new_user_email.text(),
                                student=self.student.currentItem(),
                                sex=self.new_user_sex_combo_box.currentIndex(),
                                professor=self.professor)

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

        admins: List[Administration] = list(map(lambda x: x.admin, self.professor.admins))

        for admin in admins:
            self.tableWidget.add_row(admin)

    def show_parent_table(self):
        self.tableWidget_2.clear()

        parents: List[Parent] = filter(lambda x: x is not None, (map(lambda x: x.parents, self.professor.students)))
        print(parents)

        for parent in parents:
            self.tableWidget_2.add_row(parent)

    def on_user_type_changed(self, current_index):
        self.student_label.setHidden(current_index != UserType.PARENT)
        self.student.setHidden(current_index != UserType.PARENT)
