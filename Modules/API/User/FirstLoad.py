from datetime import datetime
from typing import Dict, Type

from DataBase2 import Auth, Semester, DBObject, IListed, Professor, UserType, Session, ISession
from Domain.Exception.Authentication import UnauthorizedError
from Modules.API import AccessError
from Modules.API.User import UserAPI
from Modules.utils import synch_foreach


class FirstLoad(UserAPI):
    __address__ = UserAPI.__address__ + '/first_load'

    @classmethod
    def load(cls, auth: Auth, on_finish=None, on_error=None):
        from Client.MyQt.Widgets.Network.BisitorRequest import QBisitorRequest
        def apply(received_data):
            def create_row(session: ISession, item_data: Dict, class_: Type[DBObject]):
                if not class_.get(session, **item_data):
                    new_record = class_(**item_data)
                    session.add(new_record)

            # received_data = ServerFirstLoadData(**data)
            session = Session()

            auth = Auth(**received_data.pop('Auth'))
            session.add(auth)
            session.flush()

            professor = Professor(**received_data.pop('Professor')[0])

            professor._last_update_in = datetime.now()
            professor._last_update_out = datetime.now()
            session.add(professor)
            session.flush()

            synch_foreach(session, received_data, create_row)

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
        if auth.user_type_id == UserType.PROFESSOR:
            return self.first_load_data(auth)
        else:
            raise AccessError()

    def first_load_data(self, auth):
        professor = auth.user
        professor_id = professor.id
        main_data = dict()
        current_semester = Semester.current(professor)

        for cls in DBObject.__subclasses__():
            if cls.__name__ == Auth.__name__:
                main_data[cls.__name__] = self.session. \
                    query(Auth). \
                    filter(Auth.user_type_id == UserType.PROFESSOR). \
                    filter(Auth.user_id == professor_id). \
                    first()
            else:
                try:
                    if issubclass(cls, IListed):
                        main_data[cls.__name__] = cls.all(professor.session())
                    else:
                        main_data[cls.__name__] = cls.of(professor, semester=current_semester)
                except UnauthorizedError:
                    pass

        return main_data
