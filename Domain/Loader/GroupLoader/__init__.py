from typing import List, NamedTuple


class GroupLoader:
    class student(NamedTuple):
        first_name: str
        last_name: str
        middle_name: str = ''

    def get_group_name(self) -> str:
        raise NotImplementedError()

    def get_students_list(self) -> List[student]:
        raise NotImplementedError()
