from Parser.ServerConfiguration.Database import DatabaseConfig
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
        self.database = DatabaseConfig()
        self.notification = NotificationConfig()
        self.server = ServerConfig()
        self.logging = LoggingConfig()