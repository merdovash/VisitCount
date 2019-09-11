import os
import sys
from pathlib import Path


class _DatabaseConfig:
    schema = None

    def connection_string(self):
        res = {
            'drivername': 'sqlite',
            'query': {}
        }

        if hasattr(self, 'schema'):
            res['drivername'] = self.schema
            if self.schema == 'mysql':
                res['query'].update({'charset': 'utf8'})

        if hasattr(self, '_login'):
            res['login'] = self._login

        if hasattr(self, '_password'):
            res['password'] = self._password

        if hasattr(self, '_host'):
            res['host'] = self._host
        else:
            db_path = Path(__file__).parent / 'db2.db'
            res['host'] = '/{}'.format(db_path.as_posix())

        if hasattr(self, '_database'):
            res['database'] = self.schema

        if hasattr(self, 'query'):
            res['query'].update(self.query)

        return '{}://{}/{}'.format(
            res['drivername'],
            '{}{}'.format(
                '{}:{}@'.format(
                    res['login'],
                    res['password']
                ) if res['password'] else (
                    '{}@'.format(
                        res['login']
                    ) if res['login'] else ''),
                res['host']
            ),
            res['database']
        )


class DatabaseCLIConfig(_DatabaseConfig):
    __slots__ = ('_login', '_password', '_database', '_host', 'schema')

    def __init__(self):
        if 'DATABASE_URL' in os.environ:
            self._from_environ()
        else:
            self._from_argv()

    def _from_environ(self):
        from urllib.parse import urlparse
        parser = urlparse(os.environ.get('DATABASE_URL'))
        self.schema = parser.scheme
        self._host = parser.netloc
        self._database = parser.path[1:]

    def _from_argv(self):
        import argparse
        parser = argparse.ArgumentParser()
        parser.add_argument('-database-login', type=str, dest="database_login")
        parser.add_argument('-database-password', type=str, dest="database_password")
        parser.add_argument('-database-database', type=str, dest="database_database")
        parser.add_argument('--database-host', type=str, dest="database_host", default='localhost')
        parser.add_argument('--database-server', type=str, dest="database_server", default='postgres',
                            choices=['mysql', 'postgres'])

        res, _ = parser.parse_known_args(sys.argv)

        self._login = res.database_login
        self._password = res.database_password
        self._database = res.database_database
        self._host = res.database_host
        self.schema = res.database_server


class DatabaseINIConfig(_DatabaseConfig):
    def __init__(self, path):
        import configparser
        config = configparser.ConfigParser()
        print(Path(path).absolute())
        config.read(str(Path(path).absolute()))

        data = config['DATABASE']

        self._login = data['login']
        self._password = data.get('password')
        self._host = data['host']
        self._database = data['database']
        self.schema = data['schema']
