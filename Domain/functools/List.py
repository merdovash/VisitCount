from sqlalchemy.ext.associationproxy import _AssociationList


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
