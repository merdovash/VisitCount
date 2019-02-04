from typing import List, Dict

from DataBase2 import _DBPerson
from Domain.Structures.DictWrapper import Structure
from Domain.Structures.DictWrapper.Network import BaseRequest
from Domain.Structures.PrimitiveWrapper import ID
from Domain.Validation.Values import Get


class Reciever(Structure):
    id: ID
    class_name: str

    def __init__(self, id, class_name):
        super().__init__()
        self.id = Get.int(id)
        self.class_name = Get.table_name(class_name)


class NotificationResponse(Structure):
    success_count: int = None
    wrong_emails: List[Reciever]

    def __init__(self, success_count, wrong_emails):
        self.success_count = Get.int(success_count)

        if all(isinstance(item, Reciever) for item in wrong_emails):
            self.wrong_emails = wrong_emails
        else:
            self.wrong_emails = [Reciever(**data) for data in wrong_emails]


class NotificationRequest(BaseRequest):
    def __init__(self, user: _DBPerson, data):
        super().__init__(user)
        self.data = data
