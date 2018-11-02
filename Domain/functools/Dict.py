def without(d, *keys) -> dict:
    new_dict = {}

    for key in d:
        if key not in keys:
            new_dict[key] = d[key]

    return new_dict
