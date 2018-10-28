from DataBase2 import Auth, Update
from Modules import Module
from Modules.Synch import address
from Parser.JsonParser import to_db_object
from Server.Response import Response


class Sycnh(Module):
    def __init__(self, app, request):
        super().__init__(app, request, address)

    def post(self, data: dict, response: Response, auth: Auth, **kwargs):
        new_id_map = {}

        print('enter', data)
        with self.db.no_autoflush:
            for action_type in [Update.ActionType.UPDATE, Update.ActionType.NEW, Update.ActionType.DELETE]:
                changes = data[str(action_type)]

                for table in changes:
                    for row in changes[table]:
                        if action_type == Update.ActionType.NEW:
                            object_ = to_db_object(table, row)
                            new_id_map[row['new_index']] = object_.id

                        if action_type == Update.ActionType.UPDATE:
                            exec(f'from DataBase2 import {table}')
                            TableModel = eval(table)
                            object_ = self.db.query(TableModel).filter(TableModel.id == row['id']).first()

                            columns = list(map(lambda x: x.name, object_.__table__._columns))

                            for column_name in columns:
                                obj_vale = object_.__getattribute__(column_name)
                                new_obj_value = int(row[column_name]) if row[column_name].isnumeric() else row[
                                    column_name]

                                if obj_vale != new_obj_value:
                                    setattr(object_, column_name, new_obj_value)

                        if action_type == Update.ActionType.DELETE:
                            object_ = self.db.query(eval(table)).filter(eval(table).id == row['id']).first()

                            self.db.delete(object_)

        self.db.commit()
        self.db.flush()

        print('map', new_id_map)
        response.set_data(new_id_map)
