from DataBase2 import Professor, Lesson, Group, LessonsGroups, \
    StudentsGroups, Student, Discipline, Visitation, Auth, UserType
from Modules import Module
from Modules.FirstLoad import address


class FirstLoadModule(Module):
    def __init__(self, app, request, db):
        super().__init__(app, request, db, address)

    def post(self, data, response, auth, **kwargs):
        print('first_load', auth)
        if auth.user_type == 1:
            response.set_data(
                self.first_load_data(professor_id=auth.user_id)
            )
        else:
            response.set_error('no such privileges')

    def first_load_data(self, professor_id):
        return dict(Auth=self.db
                    .query(Auth)
                    .filter(Auth.user_type == UserType.PROFESSOR)
                    .filter(Auth.user_id == professor_id)
                    .all(),
                    Professor=self.db
                    .query(Professor)
                    .filter(Professor.id == professor_id).all(),
                    Lesson=self.db
                    .query(Lesson)
                    .filter(Lesson.professor_id == professor_id)
                    .all(),
                    LessonsGroups=self.db
                    .query(LessonsGroups)
                    .join(Lesson)
                    .filter(Lesson.professor_id == professor_id)
                    .all(),
                    Group=self.db
                    .query(Group)
                    .join(LessonsGroups)
                    .join(Lesson)
                    .filter(Lesson.professor_id == professor_id)
                    .all(),
                    StudentsGroups=self.db
                    .query(StudentsGroups)
                    .join(Group)
                    .join(LessonsGroups)
                    .join(Lesson)
                    .filter(Lesson.professor_id == professor_id)
                    .all(),
                    Student=self.db
                    .query(Student)
                    .join(StudentsGroups)
                    .join(Group)
                    .join(LessonsGroups)
                    .join(Lesson)
                    .filter(Lesson.professor_id == professor_id)
                    .all(),
                    Discipline=self.db
                    .query(Discipline)
                    .join(Lesson)
                    .filter(Lesson.professor_id == professor_id)
                    .all(),
                    Visitation=self.db
                    .query(Visitation)
                    .join(Lesson)
                    .filter(Lesson.professor_id == professor_id)
                    .all())
