from Modules.FirstLoad.ClientSide import FirstLoad
from Modules.NotificationModule.ClientSide import Notification


def run_notification(login, password, host, **kwargs):
    Notification(login, password, host, **kwargs).start()


def first_load(login, password, host, **kwargs) -> None:
    assert isinstance(login, str), f'object {login} is not str'
    assert isinstance(password, str), f'object {password} is not str'

    FirstLoad(host, login, password, **kwargs).start()
