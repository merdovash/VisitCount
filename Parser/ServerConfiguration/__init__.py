import sys

from Parser.ServerConfiguration.Database import DatabaseCLIConfig, DatabaseINIConfig
from Parser.ServerConfiguration.Logging import LoggingConfig
from Parser.ServerConfiguration.Notification import NotificationConfig
from Parser.ServerConfiguration.Server import ServerConfig


def Config():
    global __config
    if __config is None:
        __config = _Config()
    return __config


__config = None


class _Config:
    def __init__(self):
        import argparse

        parser = argparse.ArgumentParser()
        parser.add_argument('-DATABASE', type=str)

        res, _ = parser.parse_known_args(sys.argv)

        if res.DATABASE:
            self.database = DatabaseINIConfig(res.DATABASE)
        else:
            self.database = DatabaseCLIConfig()
        self.notification = NotificationConfig()
        self.server = ServerConfig()
        self.logging = LoggingConfig()