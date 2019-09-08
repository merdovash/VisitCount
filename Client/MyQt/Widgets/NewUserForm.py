from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QFormLayout, QLineEdit, QCheckBox, QPushButton, QHBoxLayout, \
    QMessageBox

from Client.MyQt.Widgets.Network.BisitorRequest import QBisitorRequest
from Client.MyQt.Widgets.QLink import QLink
from Modules.API.User.Professor.NewProfessor import ProfessorCreateAPI
from Modules.NewProfessor import NewProfessorResponse


class NewUserForm(QWidget):
    def __init__(self, flags=None, *args, **kwargs):
        super().__init__(flags, *args, **kwargs)
        with open('Client/src/style.qss', 'r') as style_file:
            self.setStyleSheet(style_file.read())

        layout = QVBoxLayout()

        title = QLabel('Создание новой учетной записи Преподавателя')
        layout.addWidget(title)

        form = QFormLayout()

        login = QLineEdit()
        form.addRow(QLabel('Логин*'), login)

        password = QLineEdit()
        password.setEchoMode(QLineEdit.Password)
        form.addRow(QLabel('Пароль*'), password)

        last_name = QLineEdit()
        form.addRow(QLabel('Фамилия*'), last_name)

        first_name = QLineEdit()
        form.addRow(QLabel('Имя*'), first_name)

        middle_name = QLineEdit()
        form.addRow(QLabel('Отчество'), middle_name)

        email = QLineEdit()
        form.addRow(QLabel('email'), email)

        agreement = QCheckBox()
        form.addRow(agreement, QLink('Я даю согласие на обработку персональных данных',
                                     'http://bisitor.itut.ru/personal_agreement'))

        layout.addLayout(form)

        btn_layout = QHBoxLayout()

        ok_btn = QPushButton('Продолжить')
        btn_layout.addWidget(ok_btn)

        cancel_btn = QPushButton('Отменить')
        btn_layout.addWidget(cancel_btn)

        layout.addLayout(btn_layout)

        def on_ok():
            def on_success(*args):
                QMessageBox().information(self, 'Создание учетной записи', 'Создание учетной записи прошло успешно')
                self.close()

            def on_error(response):
                if response.message == 'login':
                    QMessageBox().information(self, 'Созданиеучетной записи', 'Логин уже занят. Введите дургой логин')
                    login.setText('')
                else:
                    QMessageBox().information(self, 'Созданиеучетной записи', f'Неизвестная ошибка {response.message}')
                    print(response.message)

            val = {'Логин': login.text() != '',
                   'Пароль': password.text() != '',
                   'Фамилия': last_name.text() != '',
                   'Имя': first_name.text() != '',
                   'Согласие': agreement.isChecked()}
            if any(not v for v in val.values()):
                QMessageBox().information(
                    self,
                    'Необходимо заполнить все поля',
                    f'Для продолжения необходимо заполнить поля {", ".join([key for key, value in val.items() if not value])}'
                )
            else:
                self.manager = ProfessorCreateAPI.create(
                    {
                        'login': login.text(),
                        'password': password.text(),
                        'last_name': last_name.text(),
                        'first_name': first_name.text(),
                        'middle_name': middle_name.text(),
                        'email': email.text()
                    },
                    on_success,
                    on_error
                )
        ok_btn.clicked.connect(on_ok)

        def on_cancel():
            self.close()

        cancel_btn.clicked.connect(on_cancel)

        self.setLayout(layout)
