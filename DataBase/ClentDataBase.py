import datetime

from Client.test import safe
from DataBase.sql_handler import DataBase, DataBaseWorker


class ClientDataBase(DataBaseWorker):
    def add_visit(self, student_id: int, lesson_id: int):
        new_visit = {
            DataBase.Schema.visitations.name: [
                {
                    DataBase.Schema.visitations.columns.student_id.name: student_id,
                    DataBase.Schema.visitations.columns.lesson_id.name: lesson_id
                }
            ]
        }
        self.set_updates(data=new_visit)

    @safe
    def complete_lesson(self, lesson_id: int):
        r = self.sql_request("UPDATE {0} SET completed=1 WHERE id={1}",
                             self.config.lessons,
                             lesson_id)
        return r

    @safe
    def update_lesson_date(self, lesson_id: int, new_date: datetime):
        # TODO send update on server
        data = {
            DataBase.Schema.lessons.name: [
                {
                    DataBase.Schema.lessons.columns.id.name: lesson_id,
                    DataBase.Schema.lessons.columns.date.name: new_date
                }
            ]
        }
        self.set_updates(data)

    @safe
    def start_lesson(self, lesson_id=None):
        req = "UPDATE {} SET completed=1 WHERE id={}"
        params = [self.config.lessons, lesson_id]

        res = self.sql_request(req, *tuple(params))

        return res

    def add_card_id_to(self, card_id: int, student_id: int) -> None:
        update_card_id = {
            DataBase.Schema.students.name: [
                {
                    DataBase.Schema.students.columns.card_id.name: card_id,
                    'id': student_id
                }
            ]
        }
        self.set_updates(update_card_id)
