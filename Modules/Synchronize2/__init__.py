from Modules import Keys

address = "/synchronize2"


class Key(Keys):
    CLIENT_ACCEPT_UPDATES_COUNT = Keys('rows_affected')
    updates_removed = Keys('updates_removed')
