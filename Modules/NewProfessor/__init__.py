from Domain.Structures.DictWrapper import Structure

address = '/new_professor'


class NewProfessorRequest(Structure):
    login: str
    password: str
    first_name: str
    last_name: str
    middle_name: str

    def __init__(self, login, password, last_name, first_name, middle_name):
        self.login = login
        self.password = password
        self.last_name = last_name
        self.first_name = first_name
        self.middle_name = middle_name


class NewProfessorResponse(Structure):
    ok = 'ok'

    def __init__(self, ok):
        self.ok = ok
