from DataBase2 import Professor, Lesson, Group, LessonsGroups, \
    StudentsGroups, Student, Discipline, Visitation, Auth, UserType, Administration, NotificationParam
from Modules import Module
from Modules.FirstLoad import address


class FirstLoadModule(Module):
    def __init__(self, app, request):
        super().__init__(app, request, address)

    def post(self, data, response, auth, **kwargs):
        print('first_load', auth)
        if auth.user_type == 1:
            response.set_data(
                self.first_load_data(professor_id=auth.user_id)
            )
        else:
            response.set_error('no such privileges')

    def first_load_data(self, professor_id):
        professor = self.session.query(Professor).filter_by(id=professor_id).first()
        return dict(Auth=self.session
                    .query(Auth)
                    .filter(Auth.user_type == UserType.PROFESSOR)
                    .filter(Auth.user_id == professor_id)
                    .all(),
                    Professor=self.session
                    .query(Professor)
                    .filter(Professor.id == professor_id).all(),
                    Lesson=self.session
                    .query(Lesson)
                    .filter(Lesson.professor_id == professor_id)
                    .all(),
                    LessonsGroups=self.session
                    .query(LessonsGroups)
                    .join(Lesson)
                    .filter(Lesson.professor_id == professor_id)
                    .all(),
                    Group=self.session
                    .query(Group)
                    .join(LessonsGroups)
                    .join(Lesson)
                    .filter(Lesson.professor_id == professor_id)
                    .all(),
                    StudentsGroups=self.session
                    .query(StudentsGroups)
                    .join(Group)
                    .join(LessonsGroups)
                    .join(Lesson)
                    .filter(Lesson.professor_id == professor_id)
                    .all(),
                    Student=self.session
                    .query(Student)
                    .join(StudentsGroups)
                    .join(Group)
                    .join(LessonsGroups)
                    .join(Lesson)
                    .filter(Lesson.professor_id == professor_id)
                    .all(),
                    Discipline=self.session
                    .query(Discipline)
                    .join(Lesson)
                    .filter(Lesson.professor_id == professor_id)
                    .all(),
                    Visitation=self.session
                    .query(Visitation)
                    .join(Lesson)
                    .filter(Lesson.professor_id == professor_id)
                    .all(),
                    Administration=Administration.of(professor),
                    NotificationParam=NotificationParam.of(professor))
