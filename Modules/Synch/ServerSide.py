from DataBase2 import Auth, Discipline, StudentsGroups, Student, Group, Professor, Visitation, Lesson, \
    Parent, NotificationParam, Administration, ActionType
from Domain.Action.SynchAction import add_new_rows, sync_rows, delete_rows
from Domain.functools.Dict import fix_keys
from Modules import Module
from Modules.Synch import address
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
        print('raw', data)
        updates_dict = fix_keys(data)
        print(updates_dict)
        with self.session.no_autoflush:
            new_id_map = add_new_rows(updates_dict[ActionType.NEW], self.session, auth.user.id)
            sync_rows(updates_dict[ActionType.UPDATE], self.session, auth.user.id)
            delete_rows(updates_dict[ActionType.DELETE], self.session, auth.user.id)

        self.session.commit()
        self.session.flush()

        print('map', new_id_map)

        response.set_data(new_id_map)
