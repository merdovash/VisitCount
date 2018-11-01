from DataBase2 import Session, Update, Professor, ProfessorsUpdates
from Domain.Prepare import get_updated_object


def create_professors_update(update_id, performer_id):
    assert isinstance(update_id, int), f'object {update_id} is not id (int)'

    session = Session()

    update = session.query(Update).filter_by(id=update_id).first()

    updated_object = get_updated_object(update, session)

    professors = list(filter(lambda professor: professor.id != performer_id, Professor.of(updated_object)))

    for professor in professors:
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
