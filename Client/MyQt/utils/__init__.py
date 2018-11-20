class Signaler:
    def __init__(self):
        self.listeners = []

    def __iadd__(self, other):
        self.listeners.append(other)
        return self

    def __call__(self, *args, **kwargs):
        for listener in self.listeners:
            listener(*args, **kwargs)
