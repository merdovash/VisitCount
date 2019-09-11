import argparse
import sys


class NotificationConfig:
    def __init__(self):
        parser = argparse.ArgumentParser()
        parser.add_argument('-notification-email', type=str, dest="notification_email")
        parser.add_argument('-notification-password', type=str, dest="notification_password")
        parser.add_argument('-notification-smtp-server', type=str, dest="smtp_server", default="smtp.gmail.com:587")

        res, _ = parser.parse_known_args(sys.argv)

        self.password = res.notification_password
        self.email = res.notification_email
        self.server = res.smtp_server