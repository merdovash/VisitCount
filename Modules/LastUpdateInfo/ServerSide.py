from sqlalchemy import or_

from DataBase2 import Auth, Professor, _DBTrackedObject
from Domain.Structures.DictWrapper.Network.Synch import Changes
from Modules import Module
from Modules.LastUpdateInfo import address
from Server.Response import Response


class LastUpdateInfo(Module):
    def __init__(self, app, request):
        super().__init__(app, request, address)

    def post(self, data: dict, response: Response, auth: Auth, **kwargs):
        professor: Professor = auth.user
        assert isinstance(professor, Professor)

        last_update = professor._last_update_out
        items = {'created': {}, 'updated': {}, 'deleted': {}}
        for cls in _DBTrackedObject.subclasses():
            updated = professor.session() \
                .query(cls) \
                .filter(cls._updated > professor._last_update_out) \
                .all()
            created = professor.session() \
                .query(cls) \
                .filter(cls._created > professor._last_update_out) \
                .all()
            deleted = professor.session() \
                .query(cls) \
                .filter(cls._deleted > professor._last_update_out) \
                .all()
            items['updated'][cls.__name__] = updated
            items['created'][cls.__name__] = created
            items['deleted'][cls.__name__] = deleted

        changes = Changes(**items)

        if len(changes) > 0:
            response.set_data(changes)
        else:
            response.set_error('no changes')

