from enum import Enum
from pathlib import Path
from typing import List


class Reader:
    suffix: List[str] = []

    @classmethod
    def check(cls, file):
        if not isinstance(file, Path):
            file = Path(file)

        return file.suffix in cls.suffix


class WordReader(Reader):
    suffix = ['.docx']

    class Mode(Enum):
        LIST = 0
        LIST_IN_TABLE = 1
