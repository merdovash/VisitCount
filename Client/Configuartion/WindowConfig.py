import io
import json
import os

from Client.Configuartion.Configurable import Configurable
from Client.test import safe


class Config:
    def __init__(self, path=os.path.abspath("window_config.json")):
        self.path = path
        self.professor_id = None
        try:
            with io.open(path, "r", encoding='utf-8') as file:
                self.obj = json.load(file)
                print('open config:', self.obj)
        except FileNotFoundError as e:
            print('file not found')
            self.obj = {}

    def set_professor_id(self, professor_id):
        professor_id = str(professor_id)
        if professor_id in self.obj.keys():
            pass
        else:
            self.obj[professor_id] = {}
        self.professor_id = professor_id

    def log_out(self):
        self.professor_id = None

    def check(self, a: Configurable):
        if self.professor_id is not None:
            a.check(self.obj[self.professor_id])

    def new_user(self, professor_id):
        if str(professor_id) not in self.obj:
            self.obj[str(professor_id)] = {}

    def __contains__(self, item):
        if self.professor_id is None:
            return item in self.obj
        else:
            return item in self.obj[self.professor_id]

    def __getitem__(self, item):
        if self.professor_id is None:
            if isinstance(item, int):
                return self.obj[str(item)]
            elif isinstance(item, str):
                if item in self.obj.keys():
                    return self.obj[item]
                return None
        else:
            return self.obj[self.professor_id][item]

    def __setitem__(self, key, value):
        if self.professor_id is None:
            self.obj[key] = value
        else:
            self.obj[self.professor_id][key] = value

    @safe
    def sync(self):
        print('synching', self.obj)
        with io.open(self.path, 'w+', encoding='utf-8') as outfile:
            json.dump(self.obj, outfile, ensure_ascii=False)

    def __repr__(self):
        if self.professor_id is None:
            return self.obj.__repr__()
        else:
            return self.obj[self.professor_id].__repr__()

    def __len__(self):
        return len(self.obj)


def load(path: str = None) -> Config:
    if path is None:
        return Config()
    return Config(path)


if __name__ == "__main__":
    window_config = load()
    print(window_config)
    window_config.sync()
