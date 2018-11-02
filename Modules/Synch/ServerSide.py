from DataBase2 import Auth, UpdateType
from Domain.functools.Dict import without
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
        updates_dict = data['total_dict']
        with self.session.no_autoflush:
            for action_type in [UpdateType.UPDATE, UpdateType.NEW, UpdateType.DELETE]:
                changes = updates_dict.get(str(action_type), {})
                changes.update(updates_dict.get(action_type, {}))

                for table in changes:
                    exec(f'from DataBase2 import {table}')
                    TableModel = eval(table)
                    for row in changes[table]:
                        if action_type == UpdateType.NEW:
                            object_ = to_db_object(table, without(row, 'id'))
                            self.session.add(object_)
                            self.session.commit()
                            new_id_map[row['new_index']] = object_.id

                        if action_type == UpdateType.UPDATE:

                            object_ = self.session.query(TableModel).filter(TableModel.id == row['id']).first()

                            columns = list(map(lambda x: x.name, object_.__table__._columns))

                            for column_name in columns:
                                obj_vale = object_.__getattribute__(column_name)
                                new_obj_value = int(row[column_name]) if row[column_name].isnumeric() else row[
                                    column_name]

                                if obj_vale != new_obj_value:
                                    setattr(object_, column_name, new_obj_value)

                        if action_type == UpdateType.DELETE:
                            object_ = self.session.query(TableModel).filter(TableModel.id == row['id']).first()

                            self.session.delete(object_)

        self.session.commit()
        self.session.flush()

        print('map', new_id_map)
        response.set_data(new_id_map)
