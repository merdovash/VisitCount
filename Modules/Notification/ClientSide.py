from typing import Dict, Type

from sqlalchemy import inspect

from DataBase2 import _DBPerson
from Domain.Structures.DictWrapper.Network.Notification import NotificationRequest, NotificationResponse
from Modules.Client import ClientWorker
from Modules.Notification import address
from Domain.functools.Format import agree_to_number


class NotificationSender(ClientWorker):
    def on_response(self, received_data: Dict, progress_bar):
        response = NotificationResponse(**received_data)

        message = f'Успешно отправлено {response.success_count} {agree_to_number("письмо", response.success_count)}.'
        if len(response.wrong_emails) > 0:
            message += '\n\nСледующим пользователям письма не были доставленны из-за неверного email-адреса:'

            for index, person in enumerate(response.wrong_emails, 1):
                class_: Type[_DBPerson] = _DBPerson.class_(person.class_name)
                user: _DBPerson = class_.get(self.session, id=person.id)

                message += f'\n  {index}. {user.type_name} {user.full_name()}, email: {user.email}'

        self.finish.emit(message)

    def __init__(self, professor, host):
        super().__init__()
        self.session = inspect(professor).session
        self.address = host + address
        self.data = NotificationRequest(professor, {})
