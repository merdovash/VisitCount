from typing import List

from DataBase2 import Student, Group


class GroupLoader:
    def get_group(self) -> Group:
        raise NotImplementedError()

    def get_students_list(self) -> List[Student]:
        raise NotImplementedError()
