class InvalidLogin(Exception):
    def __init__(self, msg='no such login'):
        super().__init__(f"Invalid login: {msg}")


class InvalidPassword(Exception):
    def __init__(self, msg=None):
        super().__init__(f'Invalid password {msg}')