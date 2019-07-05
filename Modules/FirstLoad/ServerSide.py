from DataBase2 import Professor, Lesson, Group, LessonsGroups, \
    StudentsGroups, Student, Discipline, Visitation, Auth, Administration, Parent, _DBObject, _DBList, Semester
from Domain.Exception.Authentication import UnauthorizedError
from Domain.Structures.DictWrapper.Network.FirstLoad import ServerFirstLoadData
from Modules import Module
from Modules.FirstLoad import address


class FirstLoadModule(Module):
    def __init__(self, app, request):
        super().__init__(app, request, address)

    def post(self, data, response, auth, **kwargs):
        if auth.user_type == 1:
            response.set_data(
                self.first_load_data(auth)
            )
        else:
            response.set_error('no such privileges')

    def first_load_data(self, auth):
        professor = auth.user
        professor_id = professor.id
        main_data = dict()
        current_semester = Semester.current(professor)

        for cls in _DBObject.subclasses():
            if cls.__name__ == Auth.__name__:
                main_data[cls.__name__] = self.session. \
                    query(Auth). \
                    filter(Auth.user_type == Auth.Type.PROFESSOR). \
                    filter(Auth.user_id == professor_id). \
                    first()
            else:
                try:
                    if issubclass(cls, _DBList):
                        main_data[cls.__name__] = cls.all(professor.session())
                    else:
                        main_data[cls.__name__] = cls.of(professor, semester=current_semester)
                except UnauthorizedError:
                    pass

        r = ServerFirstLoadData(**main_data)
        return r
