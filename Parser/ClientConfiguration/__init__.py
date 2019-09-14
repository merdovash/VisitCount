from pathlib import Path

__config = None


class _Config:
    def __init__(self):
        from Client.src import src
        import argparse
        parser = argparse.ArgumentParser(description="Process parameters")
        parser.add_argument('--host', metavar='H', default='http://bisitor.itut.ru', type=str,
                            help='you can specify server host address', dest='host')
        parser.add_argument('--test', type=bool, default=False, help='for testing without Reader')
        parser.add_argument('--css', type=str, default=src.qss, help='you can disable css')

        _args, _ = parser.parse_known_args()

        self.host = _args.host
        self.css = _args.css
        self.test = _args.test

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