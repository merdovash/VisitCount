import inspect
import sys
from importlib import import_module
from typing import Dict, Type

import six

from Parser import IJSON
import Parser.JsonParser


class Structure(IJSON):
    def to_json(self):
        res = self.__dict__.copy()
        return Parser.JsonParser.JsonParser.dump(res)

    @classmethod
    def class_name(cls):
        return str(cls).split("'")[1]

    @staticmethod
    def load(data: dict, type_name: str = None,  class_: Type['Structure'] = None)->'Structure':
        def import_string(dotted_path: str):
            """
            Import a dotted module path and return the attribute/class designated by the
            last name in the path. Raise ImportError if the import failed.
            """
            try:
                module_path, class_name = dotted_path.rsplit('.', 1)
            except ValueError:
                msg = "%s doesn't look like a module path" % dotted_path
                six.reraise(ImportError, ImportError(msg), sys.exc_info()[2])

            module = import_module(module_path)

            try:
                return getattr(module, class_name)
            except AttributeError:
                msg = 'Module "%s" does not define a "%s" attribute/class' % (
                    module_path, class_name)
                six.reraise(ImportError, ImportError(msg), sys.exc_info()[2])

        if class_ is None and type_name is not None:
            class_: Type[Structure] = import_string(type_name)
        if class_ is None:
            raise TypeError('could not find class')

        if issubclass(class_, HiddenStructure):
            return class_(data)
        else:
            return class_(**data)


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
