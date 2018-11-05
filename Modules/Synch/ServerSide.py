from DataBase2 import Auth, UpdateType, Discipline, StudentsGroups, Student, Group, Professor, Visitation, Lesson, \
    Parent, NotificationParam, Administration
from Domain.Data import is_exist
from Domain.Primitives import value_of
from Domain.functools.Dict import without
from Modules import Module
from Modules.Synch import address
from Parser.JsonParser import to_db_object
from Server.Response import Response


class Sycnh(Module):
    table_order = list(map(
        lambda x: type(x).__name__,
        [Discipline(), Student(), StudentsGroups(), Group(), Professor(), Lesson(), Visitation(), Parent(),
         Administration(), NotificationParam()]))

    def __init__(self, app, request):
        super().__init__(app, request, address)
        print(self.table_order)

    def post(self, data: dict, response: Response, auth: Auth, **kwargs):
        print('enter', data)

        new_id_map = {}
        updates_dict = data['total_dict']
        with self.session.no_autoflush:
            for action_type in [UpdateType.UPDATE, UpdateType.NEW, UpdateType.DELETE]:
                changes = updates_dict.get(str(action_type), {})
                changes.update(updates_dict.get(action_type, {}))

                for table in self.table_order:
                    table_changes = changes.get(table, None)
                    if table_changes is None:
                        continue

                    exec(f'from DataBase2 import {table}')
                    TableModel = eval(table)
                    for row in table_changes:
                        if action_type == UpdateType.NEW:
                            object_ = to_db_object(table, without(row, 'id'))
                            old_exist, old = is_exist(TableModel, object_, self.session)
                            if not old_exist:
                                self.session.add(object_)
                                self.session.commit()
                                new_id_map[row['new_index']] = object_.id
                            else:
                                new_id_map[row['new_index']] = old.id

                        if action_type == UpdateType.UPDATE:

                            object_ = self.session.query(TableModel).filter(TableModel.id == row['id']).first()

                            columns = list(map(lambda x: x.name, object_.__table__._columns))

                            for column_name in columns:
                                obj_vale = object_.__getattribute__(column_name)
                                new_obj_value = value_of(row[column_name])

                                if obj_vale != new_obj_value:
                                    setattr(object_, column_name, new_obj_value)

                        if action_type == UpdateType.DELETE:
                            object_ = self.session.query(TableModel).filter(TableModel.id == row['id']).first()

                            self.session.delete(object_)

        self.session.commit()
        self.session.flush()

        print('map', new_id_map)

        response.set_data(new_id_map)
