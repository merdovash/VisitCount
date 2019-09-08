from DataBase2 import Session, Auth, Professor, ContactInfo, UserType
from Modules.NewProfessor import address, NewProfessorResponse
from Parser.JsonParser import JsonParser
from Server.Response import Response


def init(app, request):
    @app.route(address, methods=['POST'])
    def new_professor():
        print('new_professor')
        response = Response('new_professor')
        data = JsonParser.read(request.data.decode('utf8').replace("'", '"'))
        session = Session()
        duplicate_login = session.query(Auth).filter(Auth.login == data['data']['login']).all()

        if len(duplicate_login) == 1:
            response.set_error('login')
            return response()

        professor = Professor.new(session,
                                  first_name=data['data']['first_name'],
                                  last_name=data['data']['last_name'],
                                  middle_name=data['data']['middle_name'])

        contact = ContactInfo.new(session,
                                  email=data['data']['email'])

        professor.contact = contact

        session.commit()

        auth = Auth.new(session,
                        login=data['data']['login'],
                        password=data['data']['password'],
                        user_type=UserType.PROFESSOR,
                        user_id=professor.id)

        session.commit()

        response.set_data({'ok': 'ok'}, NewProfessorResponse)
        return response()

