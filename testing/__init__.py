def indexer(s: str, s2: str) -> dict:
    d = dict()
    for index, char in enumerate(s):
        if char not in d:
            try:
                s2_index = s2.index(char)
                d[char] = list()
                d[char].append(s2_index)
            except ValueError:
                pass
        else:
            try:
                s2_index = s2.index(char, d[char][-1]+1)
                d[char].append(s2_index)
            except ValueError:
                pass

    return d


def func(s1: str, s2: str) -> str:
    d1 = indexer(s1, s2)
    d2 = indexer(s2, s1)
    print(d1,d2)


if __name__ == '__main__':
    func('ABAZDC', "BACBAD")
    func("AGGTAB", "GXTXAYB")
    func("aaaa", 'aa')
    func("", "dgfdhfjk")
    func("ABBA", "ABABAC")
    func("DDDDAGDV", "ADGDV")
