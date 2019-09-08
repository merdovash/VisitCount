from Modules.API.User import UserAPI


class ProfessorAPI(UserAPI):
    __address__ = UserAPI.__address__ + '/professor'