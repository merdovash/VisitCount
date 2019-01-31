from Domain.Exception import BisitorException


class ConstraintException(BisitorException):
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


class CardIdValueException(ConstraintException):
    _title = "Ошибка ввода"
    _mask = "Во время {} была произведена попытка изменить идентифкатор карты на невозможную комбинацию.\n" \
            "Пожалуйста, убедитесь, что введены только числа."
