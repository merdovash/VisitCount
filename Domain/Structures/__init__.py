class Vector:
    def __init__(self, *args):
        assert all(map(lambda x: isinstance(x, int), args)), "values must be int"

        self.list_ = list(args)

    def __add__(self, other):
        assert len(other) == len(self), "different sizes"

        for i in range(len(self.list_)):
            self.list_[i] += other.list_[i]

    def __len__(self):
        return len(self.list_)

    def __getitem__(self, item):
        assert isinstance(item, int), "indexes must be int"
        assert item < len(self), "index is out of range"

        return self.list_[item]

    def __setitem__(self, key, value):
        assert isinstance(key, int), "index must be int"
        assert isinstance(value, int), "value must be int"
        assert key < len(self), "index is out of range"

        self.list_[key] = value
