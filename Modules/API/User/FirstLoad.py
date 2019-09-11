from datetime import datetime
from typing import Dict, Type

from DataBase2 import Auth, Semester, _DBObject, _DBList, Professor, UserType, Session
from Domain.Exception.Authentication import UnauthorizedError
from Domain.Structures.DictWrapper.Network.FirstLoad import ServerFirstLoadData
from Domain.Validation.Dict import Map
from Modules.API import AccessError
from Modules.API.User import UserAPI


class FirstLoad(UserAPI):
    __address__ = UserAPI.__address__ + '/first_load'

    @classmethod
    def load(cls, auth: Auth, on_finish=None, on_error=None):
        from Client.MyQt.Widgets.Network.BisitorRequest import QBisitorRequest
        def apply(data):
            def create_row(item_data: Dict, class_: Type[_DBObject]):
                if not class_.get(session, **item_data):
                    class_.new(session, **item_data)
                    session.flush()

            received_data = ServerFirstLoadData(**data)

            session = Session()
            auth = Auth.new(session, **received_data.auth)

            received_data.data.foreach(create_row)

            professor = Professor.new(session, **Map.item_type(received_data.professor[0], Professor))
            professor._last_update_in = datetime.now()
            professor._last_update_out = datetime.now()

            session.commit()

            if on_finish:
                on_finish()

        request = QBisitorRequest(
            cls.__address__,
            auth,
            {},
            on_finish=apply,
            on_error=on_error
        )

        return request

    def post(self, data: dict, auth: Auth, **kwargs):
        if auth.user_type == UserType.PROFESSOR:
            return self.first_load_data(auth)
        else:
            raise AccessError()

    def first_load_data(self, auth):
        professor = auth.user
        professor_id = professor.id
        main_data = dict()
        current_semester = Semester.current(professor)

        for cls in _DBObject.subclasses():
            if cls.__name__ == Auth.__name__:
                main_data[cls.__name__] = self.session. \
                    query(Auth). \
                    filter(Auth.user_type == UserType.PROFESSOR). \
                    filter(Auth.user_id == professor_id). \
                    first()
            else:
                try:
                    if issubclass(cls, _DBList):
                        main_data[cls.__name__] = cls.all(professor.session())
                    else:
                        main_data[cls.__name__] = cls.of(professor, semester=current_semester)
                except UnauthorizedError:
                    pass

        r = ServerFirstLoadData(**main_data)
        return r
