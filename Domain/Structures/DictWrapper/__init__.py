from typing import Dict

from Parser import IJSON
from Parser.JsonParser import JsonParser


class Structure(IJSON):
    def to_json(self):
        res = self.__dict__.copy()
        return JsonParser.dump(res)


class HiddenStructure(Structure):
    _data: Dict = None

    def to_json(self):
        return JsonParser.dump(self._data)

    def __getitem__(self, item):
        return self._data[item]

    def __len__(self):
        return sum([len(i) for i in self._data.values()])
