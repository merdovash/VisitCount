from pathlib import Path
from typing import Dict


def make_database_file(path: Path):
    """
    Проверяет создан ли файл базы данных

    :param path: путь к файлу базы данных
    :return: прилось ли создавать новый файл
    """
    if path.exists():
        return False

    path_to_create = []

    parent_path: Path = path.parent
    while not parent_path.exists():
        path_to_create.append(parent_path)

    for pp in path_to_create:
        pp.mkdir()

    fh = open(str(path), 'w+')
    fh.close()
    return True


def connection_config(args) -> Dict:
    res = {
        'drivername': 'sqlite',
        'query': {}
    }

    if hasattr(args, 'database_server'):
        res['drivername'] = args.database_server
        if args.database_server == 'mysql':
            res['query'].update({'charset': 'utf8'})

    if hasattr(args, 'database_login'):
        res['username'] = args.database_user

    if hasattr(args, 'database_password'):
        res['password'] = args.password

    if hasattr(args, 'database_host'):
        res['host'] = args.host
    else:
        db_path = Path(__file__).parent / 'db2.db'
        res['host'] = '/{}'.format(db_path.as_posix())
        _new = make_database_file(db_path)

    if hasattr(args, 'database_port'):
        res['port'] = args.port

    if hasattr(args, 'database_database'):
        res['database'] = args.database

    if hasattr(args, 'query'):
        res['query'].update(args.query)

    return res
