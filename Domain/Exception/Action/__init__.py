from Domain.Exception import BisitorException


class ActionException(BisitorException):
    pass


class UnnecessaryActionException(ActionException):
    pass
