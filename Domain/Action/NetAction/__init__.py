from Modules.NotificationModule.ClientSide import Notification


def run_notification(login, password, host, **kwargs):
    Notification(login, password, host, **kwargs).start()


