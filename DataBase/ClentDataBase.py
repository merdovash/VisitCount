import datetime
from typing import Dict, List, Any

from Client.test import safe
from DataBase.ServerDataBase import DataBaseWorker
from DataBase.sql_handler import DataBase


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
    def complete_lesson(self, lesson_id: int, professor_id: int):
        def lesson_not_completed():
            lesson = self.get_lessons(lesson_id=lesson_id, completed=1)
            return len(lesson) == 0

        if lesson_not_completed():
            data = {
                DataBase.Schema.lessons.name: [
                    {
                        DataBase.Schema.lessons.columns.id.name: lesson_id,
                        DataBase.Schema.lessons.columns.completed.name: 1
                    }
                ]
            }
            self.set_updates(data, professor_id)

    def register_professor_card(self, professor_id, card_id):
        data = {
            self.Schema.professors.name: [
                {
                    self.Schema.professors.columns.id.name: professor_id,
                    self.Schema.professors.columns.card_id.name: card_id
                }
            ]
        }
        self.set_updates(data, professor_id)

    @safe
    def update_lesson_date(self, lesson_id: int, new_date: datetime, professor_id: int):
        # TODO send update on server
        data = {
            DataBase.Schema.lessons.name: [
                {
                    DataBase.Schema.lessons.columns.id.name: lesson_id,
                    DataBase.Schema.lessons.columns.date.name: new_date
                }
            ]
        }
        self.set_updates(data, professor_id)

    def add_card_id_to(self, card_id: int, student_id: int, professor_id: int) -> None:
        update_card_id = {
            DataBase.Schema.students.name: [
                {
                    DataBase.Schema.students.columns.card_id.name: card_id,
                    DataBase.Schema.students.columns.id.name: student_id
                }
            ]
        }
        self.set_updates(update_card_id, professor_id)

    def get_updates(self, professor_id=None):
        def sort_by_table(updates_list) -> Dict[str, List[Dict[str, Any]]]:
            sorted_updates = {}
            for update in updates_list:
                if update[0] not in sorted_updates:
                    sorted_updates[update[0]] = []
                sorted_updates[update[0]].append(update[1])
            return sorted_updates

        updates_list = self.sql_request('SELECT {}, {} FROM {};',
                                        DataBase.Schema.updates.columns.table_name.name,
                                        DataBase.Schema.updates.columns.row_id.name,
                                        DataBase.Schema.updates.name)

        grouped_updates_list = sort_by_table(updates_list)

        updates = {}
        for table in grouped_updates_list:
            updates[table] = self.to_dict(
                self.sql_request("SELECT * FROM {0} WHERE id IN ({1})",
                                 table,
                                 ', '.join([str(i) for i in grouped_updates_list[table]])),
                table)

        return updates, len(updates_list)
