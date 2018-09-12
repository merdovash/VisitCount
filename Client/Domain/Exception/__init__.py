class NoSuchUserException(Exception):
    def __init__(self):
        super().__init__('no such user')
