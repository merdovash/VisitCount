class ConstraintException(Exception):
    pass


class ConstraintBasenameException(ConstraintException):
    def __init__(self):
        super().__init__('Base must contains fields: last_name, first_name, [Optional: middle_name]')


class ConstraintDictNameException(ConstraintException):
    def __init__(self):
        super().__init__('Dict must contain keys: "last_name", "first_name", [Optional: "middle_name"]')


class ConstraintNotEmptyException(ConstraintException):
    def __init__(self, key):
        super().__init__(f'value from {key} must be not empty')
