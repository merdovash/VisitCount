from typing import List

from DataBase2 import Student, DBObject, Auth, Group
from Domain.Structures.DictWrapper import Structure
from Modules.API import API, NoDataError


class GroupAPI(API):
    __address__ = API.__address__ + '/group'

    class GroupResponse(Structure):
        name: str
        students: List[Student]

        def __init__(self, name, students, id, **kwargs):
            self.name = name
            self.id = id
            if all([isinstance(x, Student) for x in students]):
                self.students = students
            else:
                self.students = [
                    {key: DBObject.column_type(key)(value) for key, value in student.items()}
                    for student in students
                ]

    def post(self, data: dict, auth: Auth, **kwargs):
        session = auth.session()

        group = session.query(Group).filter_by(**data, _is_deleted=False).first()
        if group is not None:
            students = Student.of(group)

            return {
                'name': group.name,
                'id': group.id,
                'students': sorted(students, key=lambda x: x.full_name())
            }
        else:
            raise NoDataError(f"группа с параметрами ({data}) не найдена")