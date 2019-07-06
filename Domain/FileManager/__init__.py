import os
import platform
import subprocess
from pathlib import Path

temp_folder = Path() / 'temp'
if not temp_folder.exists():
    temp_folder.mkdir()


def writeTempFile(data: str or bytes, suffix: str, is_bytes: bool = True) -> Path:
    folder = temp_folder / suffix
    if not folder.exists():
        folder.mkdir()

    index = len(list(folder.glob(f'*.{suffix}')))

    file_path = folder / f'file_{index}.{suffix}'

    if is_bytes:
        file_path.write_bytes(data)
    else:
        file_path.write_text(data)

    return file_path


def openFile(path):
    if platform.system() == 'Windows':
        os.startfile(path)
    elif platform.system() == 'Darwin':
        subprocess.call(('open', path))
    else:
        subprocess.call(('xdg-open', path))

