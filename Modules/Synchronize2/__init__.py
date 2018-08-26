address = "/synchronize2"


def updates_len(d:dict):
    row_affected = 0
    for table in d.keys():
        row_affected += len(d[table])

    return row_affected