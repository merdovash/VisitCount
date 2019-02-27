from DataBase2 import Professor, Lesson, Group, LessonsGroups, \
    StudentsGroups, Student, Discipline, Visitation, Auth, Administration, NotificationParam, Parent
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
        r = ServerFirstLoadData(Auth=self.session
                                .query(Auth)
                                .filter(Auth.user_type == Auth.Type.PROFESSOR)
                                .filter(Auth.user_id == professor_id)
                                .first(),
                                Professor=Professor.of(professor),
                                Lesson=Lesson.of(professor),
                                LessonsGroups=LessonsGroups.of(professor),
                                Group=Group.of(professor),
                                StudentsGroups=StudentsGroups.of(professor),
                                Student=Student.of(professor),
                                Discipline=Discipline.of(professor),
                                Visitation=Visitation.of(professor),
                                Administration=Administration.of(professor),
                                NotificationParam=NotificationParam.of(professor),
                                Parent=Parent.of(professor))
        return r
