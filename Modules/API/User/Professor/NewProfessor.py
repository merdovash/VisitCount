from DataBase2 import Auth, Session, Professor, Contact, UserType
from Modules.API.User.Professor import ProfessorAPI


class ProfessorCreateAPI(ProfessorAPI):
    __address__ = ProfessorAPI.__address__ + '/create'
    __auth_require__ = False

    @classmethod
    def create(cls, data, on_success, on_error):
        from Client.MyQt.Widgets.Network.BisitorRequest import QBisitorRequest

        request = QBisitorRequest(
            cls.__address__,
            None,
            data,
            on_finish=on_success,
            on_error=on_error
        )

        cls.requests = request

    def post(self, data: dict, auth: Auth, **kwargs):
        print('new_professor')
        session = Session()
        duplicate_login = session.query(Auth).filter(Auth.login == data['login']).all()

        if len(duplicate_login) == 1:
            raise Exception('login')

        professor = Professor.new(session,
                                  first_name=data['first_name'],
                                  last_name=data['last_name'],
                                  middle_name=data['middle_name'])

        contact = Contact.new(session,
                              email=data['email'])

        professor.contact = contact

        session.commit()

        auth = Auth.new(session,
                        login=data['login'],
                        password=data['password'],
                        user_type_id=UserType.PROFESSOR,
                        user_id=professor.id)

        session.commit()

        return {'ok': 'ok'}
