import os
import subprocess
import sys
from argparse import ArgumentParser


def install(package):
    subprocess.call([sys.executable, "-m", "pip", "install", package])


if __name__ == '__main__':
    parser = ArgumentParser()
    parser.add_argument('--db', choices=['mysql', 'postgres'])

    db_client = {
        'mysql': 'mysqlclient',
        'postgres': 'Psycopg2'
    }

    res = parser.parse_args(sys.argv[1:])

    if os.name == 'posix':
        if res.db == 'postgres':
            subprocess.call(['apt-get', 'install', 'libpq-dev', 'python-dev'])

    with open('server_requirements.txt', 'r') as req:
        for line in req:
            install(line)
        install(db_client[res.db])