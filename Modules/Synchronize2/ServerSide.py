from DataBase.ServerDataBase import DataBaseWorker
from Modules import Module
from Modules.Synchronize2 import address, Key


class Synchronize2Module(Module):
    def __init__(self, app, request, db):
        super().__init__(app, request, db, address)

    def post(self, data, response, auth, **kwargs):
        rows_affected = data[Key.CLIENT_ACCEPT_UPDATES_COUNT]
        if 1 == auth.user_type:
            if self._check(rows_affected, auth.user_id):
                self.db.remove_updates(auth.user_id)
                response.set_data({})
            else:
                response.set_error('mismatch updates count')
        else:
            response.set_error('you have no permission')

    def _check(self, rows_count, professor_id):
        current_state = self.db.sql_request("""
        SELECT count(DISTINCT {0}.{1}) 
        FROM {0}
        JOIN {2} ON {2}.{3}={0}.{1}
        WHERE {2}.{4}={5}""",
                                            DataBaseWorker.Schema.updates.name,
                                            DataBaseWorker.Schema.updates.columns.id.name,
                                            DataBaseWorker.Schema.professors_updates.name,
                                            DataBaseWorker.Schema.professors_updates.columns.update_id.name,
                                            DataBaseWorker.Schema.professors_updates.columns.professor_id.name,
                                            professor_id)[0][0]
        return current_state == rows_count
