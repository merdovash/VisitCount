import json
import re
from typing import Any

from PyQt5.QtCore import QObject
from PyQt5.QtGui import QColor

from Client.src import load_resource, resource


class _Setting:
    def __str__(self):
        return str(self.__json__())

    def __json__(self):
        raise NotImplementedError()

    def items(self):
        raise NotImplementedError()


class _SettingCustomNode(_Setting):
    def __json__(self):
        raise NotImplementedError()

    def items(self):
        raise NotImplementedError()

    def __str__(self):
        return f"<{type(self).__name__}({self.__json__()})>"


class _SettingCustomLeaf(_SettingCustomNode):
    def set(self, value):
        raise NotImplementedError()


class _SettingProxyNode(_Setting):
    def __json__(self):
        return {
            key: value.__json__() if isinstance(value, _Setting) else value
            for key, value in self.__data.items()
        }

    def items(self):
        return self.__data.items()

    __data: dict

    def __init__(self, value, parent: _Setting):
        self.__data = value
        self._parent = parent

    def __getattr__(self, item):
        return self.__data[item]


class _SettingQColor(QColor, _SettingCustomLeaf):
    _type = 'color'
    re_rgb = re.compile(r"(?:rgba?\s*\((\d+),\s?(\d+),\s?(\d+)(?:,\s?(\d+))?\))")

    def items(self):
        return [
            ('value', self.value()),
            ('default', self.default.value()),
            ('_type', 'color'),
            ('title', self.title)
        ]

    def __init__(self, d: dict, parent: _Setting):
        color_value: str or tuple = _SettingQColor.prepare_value(d['value'])
        default_color_value = _SettingQColor.prepare_value(d['default'])

        def set_default_color():
            if isinstance(default_color_value, list):
                self.default = QColor(*default_color_value)

            elif isinstance(default_color_value, str):
                self.default = QColor(default_color_value)

            else:
                raise ValueError(f"Значение по умолчанию не может быть '{d['default']}'")

        if isinstance(color_value, list):
            super().__init__(*color_value)
            set_default_color()
        elif isinstance(color_value, str):
            super().__init__(color_value)
            set_default_color()
        elif color_value is None:
            set_default_color()
            super().__init__(self.default)
        else:
            raise NotImplementedError(f"Не опреденное пведение для color: '{d['value']}' и default: '{d['default']}'")

        self.title = d['title']
        self._parentNode = parent
        self.tooltip = d.get('tooltip', None)

    def set(self, value):
        if isinstance(value, (QColor, _SettingQColor)):
            self.setRed(value.red())
            self.setGreen(value.green())
            self.setBlue(value.blue())

        else:
            raise NotImplementedError()

    def __json__(self):
        value = self.format()
        value = None if value == _SettingQColor.format(self.default) else value
        return {
            '_type': 'color',
            'title': self.title,
            'value': value,
            'default': _SettingQColor.format(self.default)
        }

    def format(self):
        return f"rgb({self.red()}, {self.green()}, {self.blue()})"

    @classmethod
    def prepare_value(cls, color_text: str):
        if color_text is None or color_text == '':
            return None

        if len(color_text) == 7 and color_text[0] == "#":
            return color_text

        if len(color_text) > 7 and color_text.startswith('rgb'):
            res = cls.re_rgb.findall(color_text)
            if res:
                return [int(v) for v in res[0] if v != '']

        raise NotImplementedError(f"Не определен способ разбора записи цвета: {color_text}")


class _SettingInt(int, _SettingCustomLeaf):
    def __json__(self):
        return {
            'title': self.title,
            'default': self.default,
            'value': int(self) if int(self) != self.default else None,
            'limits': self.limits,
            '_type': 'int'
        }

    def __init__(self, d, parent):
        super().__init__()
        self.parent = parent
        self.limits = d['limits']

    def __call__(self, d, parent):
        self.value = d['value']
        self.parent = parent
        self.title = d['title']
        self.limits = d['limits']
        self.default = d['default']
        self.__d = d

    def set(self, value):
        self.value = value

    def __int__(self):
        return self.value if self.value is not None else self.default


class Settings(_Setting):
    def items(self):
        return self.__data.items()

    __inst = None

    @classmethod
    def inst(cls) -> 'Settings':
        if cls.__inst is None:
            cls.__inst = Settings()
        return cls.__inst

    @classmethod
    def load(cls, professor):

        if professor.settings is None or professor.settings=='None':
            professor.settings = load_resource('settings.json')
            professor.session().commit()
        cls.__inst = Settings(professor.settings)
        cls.__inst.professor = professor

    def __json__(self):
        return {
            key: value.__json__()
            for key, value in self.__data.items()
        }

    def __init__(self, data=None):
        data = load_resource('settings.json', 'json') if data is None else data

        def define_class(d: dict):
            if '_type' in d.keys():
                if d['_type'] == 'color':
                    return _SettingQColor(d, self)

                if d['_type'] in ('int', 'integer'):
                    v = int.__new__(_SettingInt, d['value'] if d['value'] is not None else d['default'])
                    v(d, self)
                    return v

                if d['_type'] == 'Area':
                    return _SettingProxyNode(d, self)

                raise NotImplementedError(f"Не определен класс для _type = {d['_type']}")

            return _SettingProxyNode(d, self)

        def req(sub_d: dict or Any):
            return {
                key: define_class(req(value)) if isinstance(value, dict) else value
                for key, value in sub_d.items()
            }

        self.__data = req(data)

    def __getattr__(self, item):
        return self.__data[item]

    def save(self):
        if self.professor is not None:
            self.professor.settings = json.dumps(self.__json__())
            self.professor.session().commit()
        else:
            with open(str(resource('settings.json')), 'w+', encoding='utf8') as f:
                f.write(json.dumps(self.__json__(), ensure_ascii=False, indent=2))


if __name__ == '__main__':
    s = Settings.inst()

    print(isinstance(s.colors.visit, QColor))
    print(s)
    s.colors.visit.set(QColor("#323232"))
    print(s.colors.selected_lesson)
    print(type(s.colors.selected_lesson))
