import json

import io
import traceback

from Main.Configuartion.Configurable import Configurable


class Config:
    def __init__(self, path="window_config.json"):
        self.path = path
        self.professor_id = None
        try:
            with io.open(path, "r", encoding='utf-8') as file:
                self.obj = json.load(file)
        except FileNotFoundError as e:
            self.obj = {}

    def set_professor(self, professor_id):
        self.professor_id = professor_id

    def check(self, a: Configurable):
        if self.professor_id is not None:
            a.check(self.obj[self.professor_id])

    def new_user(self, professor_id):
        self.obj[str(professor_id)] = {}

    def __contains__(self, item):
        if self.professor_id is None:
            return item in self.obj
        else:
            return item in self.obj[self.professor_id]

    def __getitem__(self, item):
        if self.professor_id is None:
            if type(item) is int:
                return self.obj[str(item)]
            elif type(item) is str:
                return self.obj[item]
        else:
            return self.obj[self.professor_id][item]

    def __setitem__(self, key, value):
        if self.professor_id is None:
            self.obj[key] = value
        else:
            self.obj[self.professor_id][key] = value

    def sync(self):
        with open(self.path, 'w+') as outfile:
            json.dump(self.obj, outfile, ensure_ascii=False)

    def __repr__(self):
        if self.professor_id is None:
            return self.obj.__repr__()
        else:
            return self.obj[self.professor_id].__repr__()


def load(path: str = None) -> Config:
    if path is None:
        return Config()
    return Config(path)


if __name__ == "__main__":
    window_config = load()
    print(window_config)
    window_config.sync()
