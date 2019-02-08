from typing import List

from DataBase2 import Auth, Group, Student, _DBObject
from Domain.Structures.DictWrapper import Structure
from Modules import Module
from Server.Response import Response


def init(app, request):
    for api in API.__subclasses__():
        api(app, request)


class API(Module):
    def __init__(self, app, request, address):
        super().__init__(app, request, '/api' + address)


class GroupApi(API):
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
                    {key: _DBObject.column_type(key)(value) for key, value in student.items()}
                    for student in students
                ]

    def __init__(self, app, request):
        super().__init__(app, request, '/group')

    def post(self, data: dict, response: Response, auth: Auth, **kwargs):
        print('group', data)
        session = auth.session()

        group = session.query(Group).filter_by(**data, _is_deleted=False).first()
        if group is not None:
            students = Student.of(group)

            response.set_data({
                'name': group.name,
                'id': group.id,
                'students': sorted(students, key=lambda x: x.full_name())
            },
                data_type=self.GroupResponse)
        else:
            response.set_error(f"группа с параметрами ({data}) не найдена")