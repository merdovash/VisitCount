from abc import abstractmethod


class Configurable:
    @abstractmethod
    def __default__(self) -> dict:
        pass

    def check(self, a1, a2=None):
        if a2 is None:
            a2 = self.__default__()
        for key in a2:
            if key not in a1:
                print(f'key {key} not in {a1} ')
                a1[key] = a2[key]
            elif isinstance(a2[key], dict):
                self.check(a1[key], a2[key])
