from pathlib import Path

from Parser.ClientConfiguration.Database import DatabaseClientConfig
from Parser.ClientConfiguration.Host import HostClientConfig

__config = None


class _Config:
    def __init__(self):
        self.database = DatabaseClientConfig()
        self.host = HostClientConfig()

    def connection_string(self):
        import os
        import sys
        db_path = Path(os.path.abspath(os.path.dirname(sys.argv[0]))) / 'DataBase2' / 'db2.db'
        connection_string = 'sqlite:///{}'.format(db_path)
        return  connection_string


def Config():
    global __config
    if __config is None:
        __config = _Config()
    return __config