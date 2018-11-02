from DataBase2 import Session, Update, Professor, ProfessorsUpdates, UpdateType
from Domain.Prepare import get_updated_object


def create_professors_update(update_id, performer_id, professors_affected=None):
    assert isinstance(update_id, int), f'object {update_id} is not id (int)'

    session = Session()

    update = session.query(Update).filter_by(id=update_id).first()

    assert isinstance(update, Update), f'object {update} is not Update'
    updated_object = get_updated_object(update, session)

    if professors_affected is None:
        professors_affected = list(filter(lambda professor: professor.id != performer_id, Professor.of(updated_object)))

    for professor in professors_affected:
        pu = ProfessorsUpdates(professor_id=professor.id, update_id=update.id)
        session.add(pu)

    session.commit()


def create_update(updated_obj, performer_id, update_type):
    assert isinstance(performer_id, int), f'object {performer_id} is not id (int)'

    session = Session()

    update = Update(row_id=updated_obj.id,
                    table_name=type(updated_obj).__name__,
                    performer=performer_id,
                    action_type=update_type)

    session.add(update)

    session.commit()

    create_professors_update(update.id, performer_id)


def create_delete_update(deleted_object_id, deleted_object_table, performer_id, professors_affected=None):
    assert isinstance(performer_id, int), f'object {performer_id} is not id (int)'

    session = Session()

    old_create: Update = session \
        .query(Update) \
        .filter_by(table_name=deleted_object_table, row_id=deleted_object_id) \
        .first()
    if old_create is None:

        update = Update(table_name=deleted_object_table,
                        row_id=deleted_object_id,
                        performer=performer_id,
                        action_type=UpdateType.DELETE)

        session.add(update)

        session.commit()

        create_professors_update(update.id, performer_id, professors_affected)

        return update

    else:
        if old_create.action_type == UpdateType.NEW:
            session.delete(old_create)

            session.commit()
        else:
            old_create.action_type = UpdateType.DELETE

            session.commit()

            return old_create
