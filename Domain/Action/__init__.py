from DataBase2 import session_user


@session_user
def changes_ids(items, new_ids, session=None):
    assert len(items) == len(new_ids), f'{len(items)}!={len(new_ids)}'

    for item in items:
        session.merge(item)
        item.id = -item.id

    session.commit()

    for i, item in enumerate(items):
        item.id = new_ids[i]

    session.commit()

