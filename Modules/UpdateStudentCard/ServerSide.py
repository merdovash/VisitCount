from Modules import Module
from Modules.UpdateStudentCard import address


class UpdateStudentCardModule(Module):
    def __init__(self, app, request, db):
        super().__init__(app, request, db, address)

    def post(self, data, response, auth, **kwargs):
        for student in data:
            self.db.update_student_card_id(student_id=student['id'], card_id=student['card_id'])
        response.set_data(len(data))
