from Domain.Action import SynchAction
from Modules.FirstLoad.ClientSide import FirstLoad
from Modules.NotificationModule.ClientSide import Notification
from Modules.Synch.ClientSide import Synch


def run_notification(login, password, host, **kwargs):
    Notification(login, password, host, **kwargs).start()


def first_load(login, password, host, **kwargs) -> None:
    assert isinstance(login, str), f'object {login} is not str'
    assert isinstance(password, str), f'object {password} is not str'

    FirstLoad(host, login, password, **kwargs).start()


def send_updates(login, password, host, professor_id, session, **kwargs) -> None:
    assert isinstance(login, str), f'object {login} is not str'
    assert isinstance(password, str), f'object {password} is not str'
    assert isinstance(host, str), f'object {host} is not str'
    assert isinstance(professor_id, int), f'object {professor_id} is not id (int)'

    updates = SynchAction.get_all_updates(professor_id, session)
    data = SynchAction.get_updates_data(updates, session)

    Synch(
        login,
        password,
        host,
        updates,
        data,
        **kwargs
    ).start()
