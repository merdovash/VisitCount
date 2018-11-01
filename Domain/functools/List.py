from sqlalchemy.ext.associationproxy import _AssociationList


def intersect(l: list):
    total = None
    for item in l:
        assert isinstance(item, (list, set, _AssociationList)), f'items of l should be lists, but its {item}'

        if total is None:
            total = set(item)
        else:
            total = total.intersection(set(item))

    return list(total)


def flat(l: list or map) -> list:
    if isinstance(l, map):
        l = list(l)

    new_list = []
    for item in l:
        if isinstance(item, (list, _AssociationList)):
            new_list.extend(flat(item))
        else:
            new_list.append(item)

    return new_list


def unique(l: list) -> list:
    new_list = []
    for item in l:
        if isinstance(item, (list, _AssociationList)):
            item = frozenset(item)
        if item not in new_list:
            new_list.append(item)

    for i, item in enumerate(new_list):
        if isinstance(item, frozenset):
            new_list[i] = list(item)

    return new_list
