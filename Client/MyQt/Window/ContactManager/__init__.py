from typing import Set, List

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QFormLayout, QLineEdit, QPushButton, QHBoxLayout, QMessageBox

from Client.MyQt.Widgets.ComboBox.CheckComboBox import CheckableComboBox
from Client.MyQt.Widgets.Network.SendUpdate import SendUpdatesWidget
from Client.MyQt.utils import check_connection
from DataBase2 import _DBEmailObject, DataView, ContactInfo, ContactViews


class QContactManagerWindow(QWidget):
    def __init__(self, user: _DBEmailObject, flags=None, *args, **kwargs):
        assert isinstance(user, _DBEmailObject)
        super().__init__(flags, *args, **kwargs)
        self.setMinimumWidth(400)

        if user.contact is None:
            contact = ContactInfo.new(user.session())
            user.contact = contact
            user.session().commit()

        layout = QVBoxLayout()

        head = QLabel('Настройки контакта')
        layout.addWidget(head, alignment=Qt.AlignHCenter, stretch=2)

        form = QFormLayout()
        email = QLineEdit()
        email.setText(user.contact.email)

        form.addRow(QLabel('email'), email)

        data_view = CheckableComboBox()
        data_view.setItems(DataView.all())
        for view in DataView.of(user):
            data_view.setChecked(view)

        form.addRow(QLabel('Отчеты'), data_view)

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

        cancel_button.clicked.connect(cancel)

        self.setLayout(layout)
