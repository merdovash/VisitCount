import logging


class IJSON:
    def to_json(self):
        raise NotImplementedError()


import argparse

parser = argparse.ArgumentParser()
parser.add_argument('--logging_level', metavar="select logging level", default=logging.INFO, type=int)

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
parser.add_argument('--database-server', type=str, dest="database_server", default='mysql', choices=['mysql'])

server_args = parser.parse_args()
