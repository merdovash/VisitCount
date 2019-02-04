class Primitive:
    pass


class ID(int, Primitive):
    pass


class CardID(ID):
    pass


if __name__ == '__main__':
    f = CardID("4")
    print(isinstance(f, ID))
