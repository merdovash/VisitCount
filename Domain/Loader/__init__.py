from enum import Enum
from pathlib import Path
from typing import List


class Loader:
    pass


class Reader(Loader):
    suffix: List[str] = []

    @classmethod
    def check(cls, file):
        if not isinstance(file, Path):
            file = Path(file)

        return file.suffix in cls.suffix

    @classmethod
    def auto(cls, file, **kwargs):
        for class_ in cls.__subclasses__():
            if class_.check(file):
                return class_(file, **kwargs)


class WordReader(Reader):
    suffix = ['.docx']

    class Mode(Enum):
        LIST = 0
        LIST_IN_TABLE = 1



class ExcelReader(Reader):
    suffix = ['.xls', '.xlsx']


class NetworkLoader(Loader):
    _has_data = False

    def has_data(self):
        raise NotImplementedError()
