from Modules.FirstLoad.ClientSide import FirstLoad
from Modules.NotificationModule.ClientSide import Notification
from Modules.Synch.ClientSide import Synch


def run_notification(login, password, host, **kwargs):
    Notification(login, password, host, **kwargs).start()


def first_load(login, password, host, **kwargs) -> None:
    assert isinstance(login, str), f'object {login} is not str'
    assert isinstance(password, str), f'object {password} is not str'

    FirstLoad(host, login, password, **kwargs).start()


def send_updates(login, password, host, data, **kwargs) -> None:
    assert isinstance(login, str), f'object {login} is not str'
    assert isinstance(password, str), f'object {password} is not str'
    assert isinstance(host, str), f'object {host} is not str'
    assert isinstance(data, dict), f'object {data} is not dict'

    Synch(login, password, host, data, **kwargs).start()
