from collections import namedtuple, defaultdict
from typing import Dict, List, Any

from DataBase2 import Discipline, Student, StudentsGroups, Group, Professor, Lesson, Visitation, Parent, Administration, \
    NotificationParam, Update, Session, LessonsGroups, Auth, StudentsParents, ActionType
from Domain.Action import Updates
from Domain.Data import get_db_object, select, select_by_id
from Domain.Primitives import value_of
from Domain.Validation import Values
from Domain.functools.Dict import without, to_dict, fix_values
from Domain.functools.List import find
from Parser.JsonParser import to_db_object, JsonParser

table_order = list(map(
    lambda x: type(x).__name__,
    [Discipline(), Student(), Group(), Professor(), StudentsGroups(), Lesson(), LessonsGroups(), Visitation(), Parent(),
     StudentsParents(), Administration(), NotificationParam(), Auth()]))


def add_new_administration(admin_mapping, param_mapping, session, performer_id):
    item = select(session, Administration, admin_mapping)
    if item is None:
        item = Administration(**fix_values(without(admin_mapping, 'id')))

        session.add(item)
        session.commit()

        Updates.New.row(Administration, item.id, performer_id)

    param_mapping['admin_id'] = item.id

    param = NotificationParam(**fix_values(without(param_mapping, 'id')))

    session.add(param)
    session.commit()
    print('param', param)
    return item, param


def get_updates_data(updates, session):
    data = {}

    for action_type in [ActionType.NEW, ActionType.UPDATE]:
        action_updates = filter(lambda update: update.action_type == action_type, updates)

        group_by_tables = defaultdict(list)

        for update in action_updates:
            group_by_tables[update.table_name].append(to_dict(select_by_id(session, update.table_name, update.row_id)))

        data[action_type] = group_by_tables

    data[ActionType.DELETE] = defaultdict(list)
    for update in filter(lambda update: update.action_type == ActionType.DELETE, updates):
        data[ActionType.DELETE][update.table_name].append(JsonParser.read(update.extra))

    print('all updates', data)
    return data


def get_all_updates(professor_id, session):
    return session.query(Update).all()


def apply_new_indexes(new: Dict[str, List[Dict[str, Any]]], old: Dict[str, List[Dict[str, Any]]], session):
    """
    После добавления новых записей ЛБД в ЦБД, ЦБД может присн=воить другие id к записям,
    поэтому необходимо переприсвоить новые id ко всем добавленным записям

    :param new: данные о новых записях от ЦБД
    :param old: данные о новых записях от ЛБД
    :param session: сессия SQLAlchemy
    """
    prepare = namedtuple('prepare', 'object new_id')

    prepares = []

    for table_name in table_order:
        if table_name in new.keys():
            assert len(new[table_name]) == len(old[table_name]), 'dictionaries have different sizes'

            for i in range(len(new[table_name])):
                old_mapping = old[table_name][i]
                new_mapping = new[table_name][i]

                old_row = select(session, table_name, old_mapping)

                if old_row.id != new_mapping['id']:
                    old_row.id = -old_row.id

                    prepares.append(prepare(old_row, new_mapping['id']))
            else:
                session.commit()
    else:
        for p in prepares:
            p.object.id = p.new_id
            session.commit()
        else:
            session.commit()


def add_new_row(mapper, mapping, session, performer_id):
    mapping = fix_values(without(mapping, 'id', 'new_index'))

    obj = mapper(**mapping)

    _, old = get_db_object(mapper, obj, session)

    if old is None:
        session.add(obj)
        session.commit()

        Updates.New.row(mapper, obj.id, performer_id)

        return obj
    else:
        return old


def add_new_rows(data: Dict[str, List[Dict[str, Any]]], session, performer_id):
    """
    добавляет новые записи в БД

    :param data: данные о новых записях в ЛБД
    :param session: сессия SQLAlchemy
    :param performer_id: идентификтаор преподавателя, который добавил новые записи в ЛБД
    :return:
    """
    after_insert = defaultdict(list)

    print('new rows', data)

    for table_name in table_order:
        if table_name in data.keys():
            mapper = eval(table_name)

            for mapping in data[table_name]:
                print(table_name)
                if table_name == type(Administration()).__name__:
                    param_mapping = find(lambda x: x['admin_id'] == mapping['id'],
                                         data[type(NotificationParam()).__name__])
                    print(param_mapping)
                    admin_obj, param_obj = add_new_administration(
                        admin_mapping=mapping,
                        param_mapping=param_mapping,
                        session=session,
                        performer_id=performer_id)

                    print(admin_obj, param_obj)
                    after_insert[table_name].append(to_dict(admin_obj))
                    after_insert[type(NotificationParam()).__name__].append(to_dict(param_obj))
                elif table_name == type(NotificationParam()).__name__:
                    pass
                else:
                    new_obj = add_new_row(mapper, mapping, session, performer_id)
                    print(new_obj)
                    after_insert[table_name].append(to_dict(new_obj))

    return after_insert


def sync_row(obj, new_data, performer_id):
    """
    обновляет значения записи в БД

    :param obj: старый объект, существующий в БД
    :param new_data: словарь данных объекта с новыми значениями
    :param performer_id: идентификатор преподавателя, который внес изменения
    """
    changed = False

    for col in new_data.keys():
        assert isinstance(col, str), f'col {col} is not a string'
        new_value = value_of(new_data[col])
        if new_value != getattr(obj, col):
            changed = True

            setattr(obj, col, new_value)
    else:
        if changed:
            Updates.Changed.row(obj.id, Values.Get.table_name(obj), performer_id)


def sync_rows(data: Dict[str, List[Dict[str, Any]]], session, performer_id):
    """
    Синхронизирует изменения записей ЛБД и ЦБД

    :param data: данные об изменениях в ЛБД
    :param session: объект сессии
    :param performer_id: идентификатор преподавателя, который внес изменения
    """
    for table_name in table_order:
        if table_name in data.keys():
            mapper = eval(table_name)

            for mapping in data[table_name]:
                old = to_db_object(mapper, mapping)

                _, old = get_db_object(mapper, old, session)

                sync_row(old, mapping, performer_id)

    else:
        session.commit()


def delete_rows(data: Dict[str, List[Dict[str, Any]]], session, performer_id):
    """
    Удаляет записи из ЦБД, котоырй были удалены в ЛБД

    :param data: данные
    :param session: сессия SQLAlchemy
    :param performer_id: идентификатор преподавтеля, удалившего записи
    """
    for table_name in table_order:
        if table_name in data.keys():
            mapper = eval(table_name)

            for mapping in data[table_name]:
                obj = select(session, mapper, mapping)
                Updates.Delete.row(
                    deleted_object=to_dict(obj),
                    deleted_object_table=table_name,
                    performer_id=performer_id,
                    professors_affected=Professor.of(obj)
                )
                session.delete(obj)
    else:
        session.commit()


def delete_synchronized_updates(updates: List[Dict[str, Any]]):
    """
    Удаляет записи обновлений, которые были уже синхронизированы с ЦБД

    :param updates: список словарей записей об обновлениях
    """
    session = Session()

    for update_dict in updates:
        item = select(session, Update, update_dict)
        session.delete(item)
    else:
        session.commit()
