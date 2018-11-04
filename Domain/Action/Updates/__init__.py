from DataBase2 import Session, Update, UpdateType, Professor, ProfessorsUpdates
from Domain.Prepare import get_updated_object


class New:
    @staticmethod
    def row(new_row_id, performer_id):
        assert isinstance(performer_id, int), f'object {performer_id} is not id (int)'

        session = Session()

        update = Update(row_id=new_row_id.id,
                        table_name=type(new_row_id).__name__,
                        performer=performer_id,
                        action_type=UpdateType.NEW)

        session.add(update)

        session.commit()

        New.professors_update(update.id, performer_id)

    @staticmethod
    def professors_update(update_id, performer_id, professors_affected=None):
        assert isinstance(update_id, int), f'object {update_id} is not id (int)'

        session = Session()

        update = session.query(Update).filter_by(id=update_id).first()

        assert isinstance(update, Update), f'object {update} is not Update'
        updated_object = get_updated_object(update, session)

        if professors_affected is None:
            professors_affected = list(
                filter(lambda professor: professor.id != performer_id, Professor.of(updated_object)))

        for professor in professors_affected:
            pu = ProfessorsUpdates(professor_id=professor.id, update_id=update.id)
            session.add(pu)

        session.commit()


class Delete:
    @staticmethod
    def row(deleted_object_id, deleted_object_table, performer_id, professors_affected=None):
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

            New.professors_update(update.id, performer_id, professors_affected)

            return update

        else:
            if old_create.action_type == UpdateType.NEW:
                session.delete(old_create)

                session.commit()
            else:
                old_create.action_type = UpdateType.DELETE

                session.commit()

                return old_create


class Changed:
    @staticmethod
    def row(changed_row_id, table_name, performer_id):
        assert isinstance(changed_row_id, int), f'object changed_row_id {changed_row_id} should be id (int)'
        assert isinstance(performer_id, int), f'object performer_id {performer_id} should be id (int)'
        assert isinstance(table_name, str), f'table_name ({table_name}) should be str'

        session = Session()

        old = session.query(Update).filter_by(row_id=changed_row_id, table_name=table_name).first()
        if old is not None:
            return old
        else:

            update = Update(row_id=changed_row_id,
                            table_name=table_name,
                            performer=performer_id,
                            action_type=UpdateType.UPDATE)

            session.add(update)

            session.commit()

            New.professors_update(update.id, performer_id)

            return update
