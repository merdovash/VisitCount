from Domain.Exception import BisitorException

_args = None


class IJSON:
    def to_json(self):
        raise NotImplementedError()


def Args(side=None):
    global _args
    if _args is None:
        import argparse
        if side == 'client':
            from Client.src import src
            parser = argparse.ArgumentParser(description="Process parameters")
            parser.add_argument('--host', metavar='H', default='http://bisitor.itut.ru', type=str,
                                help='you can specify server host address', dest='host')
            parser.add_argument('--test', type=bool, default=False, help='for testing without Reader')
            parser.add_argument('--css', type=str, default=src.qss, help='you can disable css')

            _args = parser.parse_args()

        elif side == 'server':
            import logging
            parser = argparse.ArgumentParser()
            parser.add_argument('--logging-level', metavar="select logging level", default=logging.INFO, type=int)

            # SYSTEM
            parser.add_argument('-system-name', type=str, dest='system_name', default='Система Учета Посещаемости')
            parser.add_argument('-help-email', type=str, dest='help_email', default='Не указано')

            # SERVER
            parser.add_argument('--server-host', type=str, dest='server_host', default='0.0.0.0')
            parser.add_argument('--server-port', type=str, dest='server_port', default='5000')

            # NOTIFICATION
            parser.add_argument('-notification-email', type=str, dest="notification_email")
            parser.add_argument('-notification-password', type=str, dest="notification_password")
            parser.add_argument('-notification-smtp-server', type=str, dest="smtp_server", default="smtp.gmail.com:587")

            # DATABASE
            parser.add_argument('-database-login', type=str, dest="database_login")
            parser.add_argument('-database-password', type=str, dest="database_password")
            parser.add_argument('-database-database', type=str, dest="database_database")
            parser.add_argument('--database-host', type=str, dest="database_host", default='localhost')
            parser.add_argument('--database-server', type=str, dest="database_server", default='mysql', choices=['mysql', 'postgres'])

            _args = parser.parse_args()
        else:
            raise BisitorException("Необходимо обьявить тип приложения")
    return _args

