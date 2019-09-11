import shutil
from pathlib import Path

files = [
    'run_server.py',
    'Procfile'
]

folders = [
    'Server',
    'Parser',
    'Modules',
    'Domain',
    'DataBase2',
    'BisitorLogger'
]


def copy(file_path):
    target_path = str(Path('nc').absolute() / file_path)

    path = Path(file_path)
    if path.suffix == 'py':
        with open(target_path, 'r+') as f:
            o = f.readlines()
            o.insert(0, '# encoding: utf-8')

        with open(target_path, 'w') as f:
            f.writelines(o)

    elif path.suffix.endswith('.pyc'):
        return

    else:
        shutil.copy(file, target_path)


def copy_tree(folder):
    target_path = str(Path('nc').absolute() / folder)



for file in files:
    shutil.copy(file, str(Path('nc').absolute() / file))

for folder in folders:

    shutil.copytree(folder, str(Path('nc').absolute() / folder))