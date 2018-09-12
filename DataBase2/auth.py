from DataBase2 import Auth, session


def Authentication(login, password):
    auth = session.query(Auth).filter(Auth.login == login).filter(Auth.password == password).first()
    return auth
