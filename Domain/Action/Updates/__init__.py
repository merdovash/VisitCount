from DataBase2 import Session, Update, ActionType, Professor, ProfessorsUpdates
from Domain.Prepare import get_updated_object
from Parser.JsonParser import JsonParser


class New:
    @staticmethod
    def row(table, new_row_id, performer_id, update_type=None):
        assert isinstance(performer_id, int), f'object {performer_id} is not id (int)'
        assert isinstance(new_row_id, int), f'new_row_id {new_row_id} is not id (int)'

        if not isinstance(table, str):
            table = table.__name__

        session = Session()

        update = Update(
            row_id=new_row_id,
            table_name=table,
            performer=performer_id,
            action_type=ActionType.NEW,
            update_type=update_type)

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
    def row(deleted_object: dict, deleted_object_table, performer_id, update_type=None, professors_affected=None):
        assert isinstance(deleted_object, dict), f'deleted_object {deleted_object} is not a dict'
        assert 'id' in deleted_object.keys(), f'deleted_object {deleted_object} has no "id" key'
        assert isinstance(performer_id, int), f'object {performer_id} is not id (int)'

        session = Session()

        old_update: Update = session \
            .query(Update) \
            .filter(Update.table_name == deleted_object_table,
                    Update.row_id == deleted_object['id']) \
            .first()
        print(old_update)
        if old_update is None:

            update = Update(
                table_name=deleted_object_table,
                row_id=deleted_object['id'],
                performer=performer_id,
                action_type=ActionType.DELETE,
                extra=JsonParser.dump(deleted_object),
                update_type=update_type)

            session.add(update)

            session.commit()

            New.professors_update(update.id, performer_id, professors_affected)

            return update

        else:
            if old_update.action_type == ActionType.NEW:
                session.delete(old_update)

                session.commit()
            else:
                old_update.action_type = ActionType.DELETE

                session.commit()

                return old_update


class Changed:
    @staticmethod
    def row(changed_row_id, table_name, performer_id, update_type=None):
        assert isinstance(changed_row_id, int), f'object changed_row_id {changed_row_id} should be id (int)'
        assert isinstance(performer_id, int), f'object performer_id {performer_id} should be id (int)'
        assert isinstance(table_name, str), f'table_name ({table_name}) should be str'

        session = Session()

        old = session.query(Update).filter_by(row_id=changed_row_id, table_name=table_name).first()
        if old is not None:
            return old
        else:

            update = Update(
                row_id=changed_row_id,
                table_name=table_name,
                performer=performer_id,
                action_type=ActionType.UPDATE,
                update_type=update_type)

            session.add(update)

            session.commit()

            New.professors_update(update.id, performer_id)

            return update
