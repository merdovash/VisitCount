from PyQt5 import QtWidgets, QtCore

from Client.MyQt.Widgets.ExtendedComboBox import ExtendedCombo
from Client.MyQt.Widgets.Table.Contacts import ContactTable
from DataBase2 import Administration, Parent


class Ui_NotificationWindow(object):
    def setupUi(self, NotificationWindow):
        NotificationWindow.setObjectName("NotificationWindow")
        NotificationWindow.resize(556, 454)
        self.verticalLayout_6 = QtWidgets.QVBoxLayout(NotificationWindow)
        self.verticalLayout_6.setContentsMargins(11, 11, 11, 11)
        self.verticalLayout_6.setSpacing(6)
        self.verticalLayout_6.setObjectName("verticalLayout_6")
        self.verticalLayout = QtWidgets.QVBoxLayout()
        self.verticalLayout.setSpacing(6)
        self.verticalLayout.setObjectName("verticalLayout")
        self.main_label = QtWidgets.QLabel(NotificationWindow)
        self.main_label.setObjectName("main_label")
        self.verticalLayout.addWidget(self.main_label)
        self.tabWidget = QtWidgets.QTabWidget(NotificationWindow)
        self.tabWidget.setObjectName("tabWidget")
        self.tab_3 = QtWidgets.QWidget()
        self.tab_3.setObjectName("tab_3")
        self.horizontalLayout_2 = QtWidgets.QHBoxLayout(self.tab_3)
        self.horizontalLayout_2.setContentsMargins(11, 11, 11, 11)
        self.horizontalLayout_2.setSpacing(6)
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")
        self.formLayout = QtWidgets.QFormLayout()
        self.formLayout.setSpacing(6)
        self.formLayout.setObjectName("formLayout")
        self.label_2 = QtWidgets.QLabel(self.tab_3)
        self.label_2.setObjectName("label_2")
        self.formLayout.setWidget(0, QtWidgets.QFormLayout.LabelRole, self.label_2)
        self.new_user_type_label = QtWidgets.QLabel(self.tab_3)
        self.new_user_type_label.setObjectName("new_user_type_label")
        self.formLayout.setWidget(1, QtWidgets.QFormLayout.LabelRole, self.new_user_type_label)
        self.new_user_type_combo_box = QtWidgets.QComboBox(self.tab_3)
        self.new_user_type_combo_box.setObjectName("new_user_type_combo_box")
        self.formLayout.setWidget(1, QtWidgets.QFormLayout.FieldRole, self.new_user_type_combo_box)
        self.new_user_last_name_label = QtWidgets.QLabel(self.tab_3)
        self.new_user_last_name_label.setObjectName("new_user_last_name_label")
        self.formLayout.setWidget(3, QtWidgets.QFormLayout.LabelRole, self.new_user_last_name_label)
        self.new_user_last_name = QtWidgets.QLineEdit(self.tab_3)
        self.new_user_last_name.setObjectName("new_user_last_name")
        self.formLayout.setWidget(3, QtWidgets.QFormLayout.FieldRole, self.new_user_last_name)
        self.new_user_first_name_label = QtWidgets.QLabel(self.tab_3)
        self.new_user_first_name_label.setObjectName("new_user_first_name_label")
        self.formLayout.setWidget(4, QtWidgets.QFormLayout.LabelRole, self.new_user_first_name_label)
        self.new_user_first_name = QtWidgets.QLineEdit(self.tab_3)
        self.new_user_first_name.setObjectName("new_user_first_name")
        self.formLayout.setWidget(4, QtWidgets.QFormLayout.FieldRole, self.new_user_first_name)
        self.new_user_middle_name_label = QtWidgets.QLabel(self.tab_3)
        self.new_user_middle_name_label.setObjectName("new_user_middle_name_label")
        self.formLayout.setWidget(5, QtWidgets.QFormLayout.LabelRole, self.new_user_middle_name_label)
        self.new_user_middle_name = QtWidgets.QLineEdit(self.tab_3)
        self.new_user_middle_name.setObjectName("new_user_middle_name")
        self.formLayout.setWidget(5, QtWidgets.QFormLayout.FieldRole, self.new_user_middle_name)
        self.new_user_email_label = QtWidgets.QLabel(self.tab_3)
        self.new_user_email_label.setObjectName("new_user_email_label")
        self.formLayout.setWidget(6, QtWidgets.QFormLayout.LabelRole, self.new_user_email_label)
        self.new_user_email = QtWidgets.QLineEdit(self.tab_3)
        self.new_user_email.setObjectName("new_user_email")
        self.formLayout.setWidget(6, QtWidgets.QFormLayout.FieldRole, self.new_user_email)
        self.new_user_sex_label = QtWidgets.QLabel(self.tab_3)
        self.new_user_sex_label.setObjectName("new_user_sex_label")
        self.formLayout.setWidget(7, QtWidgets.QFormLayout.LabelRole, self.new_user_sex_label)
        self.new_user_sex_combo_box = QtWidgets.QComboBox(self.tab_3)
        self.new_user_sex_combo_box.setObjectName("new_user_sex_combo_box")
        self.formLayout.setWidget(7, QtWidgets.QFormLayout.FieldRole, self.new_user_sex_combo_box)
        self.new_user_save_btn = QtWidgets.QPushButton(self.tab_3)
        self.new_user_save_btn.setObjectName("new_user_save_btn")
        self.formLayout.setWidget(9, QtWidgets.QFormLayout.FieldRole, self.new_user_save_btn)
        self.line = QtWidgets.QFrame(self.tab_3)
        self.line.setFrameShape(QtWidgets.QFrame.HLine)
        self.line.setFrameShadow(QtWidgets.QFrame.Sunken)
        self.line.setObjectName("line")
        self.formLayout.setWidget(10, QtWidgets.QFormLayout.SpanningRole, self.line)
        self.student_label = QtWidgets.QLabel(self.tab_3)
        self.student_label.setObjectName("student_label")
        self.formLayout.setWidget(2, QtWidgets.QFormLayout.LabelRole, self.student_label)
        self.student = ExtendedCombo(self.tab_3)
        self.student.setObjectName("student")
        self.formLayout.setWidget(2, QtWidgets.QFormLayout.FieldRole, self.student)
        self.horizontalLayout_2.addLayout(self.formLayout)
        self.tabWidget.addTab(self.tab_3, "")
        self.tab_4 = QtWidgets.QWidget()
        self.tab_4.setObjectName("tab_4")
        self.verticalLayout_7 = QtWidgets.QVBoxLayout(self.tab_4)
        self.verticalLayout_7.setContentsMargins(11, 11, 11, 11)
        self.verticalLayout_7.setSpacing(6)
        self.verticalLayout_7.setObjectName("verticalLayout_7")
        self.horizontalLayout_4 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_4.setSpacing(6)
        self.horizontalLayout_4.setObjectName("horizontalLayout_4")
        self.label = QtWidgets.QLabel(self.tab_4)
        self.label.setObjectName("label")
        self.horizontalLayout_4.addWidget(self.label)
        self.admins_last_note_date_textfield = QtWidgets.QLineEdit(self.tab_4)
        self.admins_last_note_date_textfield.setObjectName("admins_last_note_date_textfield")
        self.horizontalLayout_4.addWidget(self.admins_last_note_date_textfield)
        self.verticalLayout_7.addLayout(self.horizontalLayout_4)
        self.tableWidget = ContactTable(Administration, self.tab_4)
        self.tableWidget.setObjectName("tableWidget")
        self.verticalLayout_7.addWidget(self.tableWidget)
        self.tabWidget.addTab(self.tab_4, "")
        self.tab_5 = QtWidgets.QWidget()
        self.tab_5.setObjectName("tab_5")
        self.verticalLayout_4 = QtWidgets.QVBoxLayout(self.tab_5)
        self.verticalLayout_4.setContentsMargins(11, 11, 11, 11)
        self.verticalLayout_4.setSpacing(6)
        self.verticalLayout_4.setObjectName("verticalLayout_4")
        self.verticalLayout_3 = QtWidgets.QVBoxLayout()
        self.verticalLayout_3.setSpacing(6)
        self.verticalLayout_3.setObjectName("verticalLayout_3")
        self.horizontalLayout_3 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_3.setSpacing(6)
        self.horizontalLayout_3.setObjectName("horizontalLayout_3")
        self.label_3 = QtWidgets.QLabel(self.tab_5)
        self.label_3.setObjectName("label_3")
        self.horizontalLayout_3.addWidget(self.label_3)
        self.lineEdit = QtWidgets.QLineEdit(self.tab_5)
        self.lineEdit.setObjectName("lineEdit")
        self.horizontalLayout_3.addWidget(self.lineEdit)
        self.verticalLayout_3.addLayout(self.horizontalLayout_3)
        self.verticalLayout_4.addLayout(self.verticalLayout_3)
        self.tableWidget_2 = ContactTable(Parent, self.tab_5)
        self.tableWidget_2.setObjectName("tableWidget_2")
        self.verticalLayout_4.addWidget(self.tableWidget_2)
        self.tabWidget.addTab(self.tab_5, "")
        self.verticalLayout.addWidget(self.tabWidget)
        self.horizontalLayout = QtWidgets.QHBoxLayout()
        self.horizontalLayout.setSpacing(6)
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.save_btn = QtWidgets.QPushButton(NotificationWindow)
        self.save_btn.setObjectName("save_btn")
        self.horizontalLayout.addWidget(self.save_btn)
        self.run_btn = QtWidgets.QPushButton(NotificationWindow)
        self.run_btn.setObjectName("run_btn")
        self.horizontalLayout.addWidget(self.run_btn)
        self.verticalLayout.addLayout(self.horizontalLayout)
        self.verticalLayout_6.addLayout(self.verticalLayout)

        self.retranslateUi(NotificationWindow)
        self.tabWidget.setCurrentIndex(0)
        QtCore.QMetaObject.connectSlotsByName(NotificationWindow)

    def retranslateUi(self, NotificationWindow):
        _translate = QtCore.QCoreApplication.translate
        NotificationWindow.setWindowTitle(_translate("NotificationWindow", "NotificationWindow"))
        self.main_label.setText(_translate("NotificationWindow", "Настройки параметров оповещения"))
        self.label_2.setText(_translate("NotificationWindow", "Добавить получателя"))
        self.new_user_type_label.setText(_translate("NotificationWindow", "Тип пользователя"))
        self.new_user_last_name_label.setText(_translate("NotificationWindow", "Фамилия"))
        self.new_user_first_name_label.setText(_translate("NotificationWindow", "Имя"))
        self.new_user_middle_name_label.setText(_translate("NotificationWindow", "Отчество"))
        self.new_user_email_label.setText(_translate("NotificationWindow", "e-mail"))
        self.new_user_sex_label.setText(_translate("NotificationWindow", "Пол"))
        self.new_user_save_btn.setText(_translate("NotificationWindow", "Сохранить пользователя"))
        self.student_label.setText(_translate("NotificationWindow", "Студент"))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab_3), _translate("NotificationWindow", "Новый контакт"))
        self.label.setText(_translate("NotificationWindow", "Последняя расылка производилась"))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab_4), _translate("NotificationWindow", "Администрация"))
        self.label_3.setText(_translate("NotificationWindow", "Последняя расылка производилась"))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab_5), _translate("NotificationWindow", "Родители"))
        self.save_btn.setText(_translate("NotificationWindow", "Сохранить"))
        self.run_btn.setText(_translate("NotificationWindow", "Запустить процедуру оповещения"))
