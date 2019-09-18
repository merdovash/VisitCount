import datetime
from typing import Set, List

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QFormLayout, QLineEdit, QPushButton, QHBoxLayout, QMessageBox, \
    QCheckBox, QTimeEdit, QSpinBox

from Client.MyQt.Widgets.ComboBox.CheckComboBox import CheckableComboBox
from Client.MyQt.Widgets.Network.SendUpdate import SendUpdatesWidget
from Client.MyQt.utils import check_connection
from DataBase2 import IContact, DataView, Contact, ContactViews
from Domain.MessageFormat import agree_to_number
from Modules.API.DataView import DataViewAPI


class QContactManagerWindow(QWidget):
    def __init__(self, user: IContact, flags=None, *args, **kwargs):
        assert isinstance(user, IContact)
        super().__init__(flags, *args, **kwargs)
        with open('Client/src/style.qss', 'r') as style_file:
            self.setStyleSheet(style_file.read())
        self.setMinimumWidth(500)

        if not user.contact:
            contact = Contact.new(user.session())
            user.contact = contact
            user.session().commit()

        layout = QVBoxLayout()

        head = QLabel('Настройки контакта')
        layout.addWidget(head, alignment=Qt.AlignHCenter, stretch=2)

        # Форма
        form = QFormLayout()

        # email
        email = QLineEdit()
        email.setText(user.contact.email)

        form.addRow(QLabel('email'), email)

        # отчеты
        data_view = CheckableComboBox()
        data_view.setItems(DataView.all())
        for view in DataView.of(user):
            data_view.setChecked(view)

        form.addRow(QLabel('Отчеты'), data_view)

        update_views_list_btn = QPushButton('Обновить список возможных отчетов')
        form.addRow(QLabel(''), update_views_list_btn)

        # активация
        status_label = QLabel('Отправлять отчеты')
        status_checkbox = QCheckBox()

        form.addRow(status_label, status_checkbox)

        # время
        time_input = QTimeEdit()
        form.addRow(QLabel('Время получения отчета'), time_input)
        if user.contact.last_auto is not None:
            time_input.setTime(user.contact.last_auto.time())
        else:
            time_input.setTime(datetime.time(17))

        time_delta = QSpinBox()
        time_delta.setRange(1, 5040)
        if user.contact.interval_auto_hours is not None:
            time_delta.setValue(user.contact.interval_auto_hours)
        else:
            time_delta.setValue(24)

        form.addRow(QLabel('Интервал, в часах'), time_delta)

        layout.addLayout(form)

        save_button = QPushButton("Сохранить")
        cancel_button = QPushButton("Отмена")

        button_layout = QHBoxLayout()
        button_layout.addWidget(save_button)
        button_layout.addWidget(cancel_button)

        layout.addLayout(button_layout)

        def save():
            contact = user.contact

            if contact.email != email.text():
                contact.email = email.text()

            if contact.auto != status_checkbox.isChecked():
                contact.auto = status_checkbox.isChecked()

            if contact.last_auto is None:
                contact.last_auto = datetime.datetime.now()
            if contact.last_auto.time() != time_input.time():
                contact.last_auto -= datetime.timedelta(hours=contact.last_auto.time().hour,
                                                        minutes=contact.last_auto.time().minute)
                contact.last_auto += datetime.timedelta(hours=time_input.time().hour(),
                                                        minutes=time_input.time().minute())

            contacts_views = ContactViews.of(user)
            current_views: List[DataView] = [cv._view for cv in contacts_views]
            new_views: List[DataView] = data_view.current()

            to_delete: Set[DataView] = set(current_views) - (set(current_views) & set(new_views))
            to_append: Set[DataView] = set(new_views) - (set(current_views) & set(new_views))

            for view in to_append:
                cv = ContactViews.get_or_create(
                    user.session(),
                    contact_info_id=user.contact.id,
                    data_view_id=view.id
                )
                if cv not in user.contact._views:
                    user.contact._views.append(cv)

            for view in to_delete:
                cv = ContactViews.get(
                    user.session(),
                    contact_info_id=user.contact.id,
                    data_view_id=view.id
                )
                cv.delete()

            user.session().commit()

            if check_connection():
                widget = SendUpdatesWidget(user)
                widget.show()
                widget.start.emit()
            else:
                QMessageBox().information(
                    self,
                    'Сохранение',
                    'Данные успешно сохранены в локальной базе данных.'
                    ' Подключитесь к сети, и повторите попытку для сохранения на сервере.')
            self.close()

        save_button.clicked.connect(save)

        def cancel():
            QMessageBox().information(
                self,
                'Отмена изменения контакта',
                'Внесенные изменения не были сохранены'
            )
            self.close()

        def on_update_views():
            before = DataView.all(user.session())

            def apply():
                data_view.clear()
                after = DataView.all(user.session())
                data_view.setItems(after)

                new = set(after) - set(before)
                QMessageBox().information(
                    self,
                    'Обновление списка отчётов',
                    f'Загружено {len(new)} {agree_to_number("новый", len(new))} '
                    f'{agree_to_number("вид", len(new))} {agree_to_number("отчета", len(new))}'
                    if len(new) else 'Уже загружены всё виды.')

            if check_connection():
                self.manager = DataViewAPI.load(user, apply, lambda x: print(x))
            else:
                QMessageBox().information(
                    self,
                    'Обновление списка отчётов',
                    'Не удалось установить соединение с сервером')

        update_views_list_btn.clicked.connect(on_update_views)

        cancel_button.clicked.connect(cancel)

        self.setLayout(layout)
