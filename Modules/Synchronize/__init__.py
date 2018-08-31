from Modules import Keys

address = '/synchronize'


class Key(Keys):
    UPDATES = Keys('updates')
    SERVER_ACCEPT_UPDATES_COUNT = Keys('accepted_updates_count')


def updates_len(d: dict):
    row_affected = 0
    for table in d.keys():
        row_affected += len(d[table])

    return row_affected
