from typing import Dict, Type

import Parser.JsonParser
from Parser import IJSON


class Structure(IJSON):
    def to_json(self):
        res = self.__dict__.copy()
        return Parser.JsonParser.JsonParser.dump(res)

    @classmethod
    def class_name(cls):
        return str(cls).split("'")[1]

    @staticmethod
    def load(data: dict, type_name: str = None, class_: Type['Structure'] = None) -> 'Structure' or dict:
        import Modules
        try:
            if class_ is None and type_name is not None:
                class_: Type[Structure] = eval(list(filter(
                    lambda x: x == type_name,
                    [str(t).split('\'')[1] for t in Structure.__subclasses__()]))[0])
            if class_ is None:
                raise TypeError(f'could not find class {type_name}')

            if issubclass(class_, HiddenStructure):
                return class_(data)
            else:
                return class_(**data)
        except IndexError:
            return data


class HiddenStructure(Structure):
    _data: Dict = None

    def to_json(self):
        return Parser.JsonParser.JsonParser.dump(self._data)

    def __getitem__(self, item):
        return self._data[item]

    def __len__(self):
        return sum([len(i) for i in self._data.values()])

    def keys(self):
        return self._data.keys()
