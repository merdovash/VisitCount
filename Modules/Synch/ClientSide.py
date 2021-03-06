import logging
from datetime import datetime
from typing import Type, Dict, Any

from DataBase2 import _DBTrackedObject, Visitation
from Domain.Structures.DictWrapper.Network import BaseRequest
from Domain.Structures.DictWrapper.Network.Synch import ServerUpdateData, ChangeId
from Domain.functools.Function import None_or_empty
from Modules.Client import ClientWorker
from Modules.Synch import address


class Updater(ClientWorker):
    def __init__(self, professor, data, host):
        super().__init__()
        self.data = BaseRequest(professor, data)
        if host[:4] != 'http':
            host = 'http://' + host
        self.address = host + address
        self.professor = professor

    def on_response(self, data, progress_bar):
        """

        :param data: {
            changed_id: {
                class_name: [ {'from_id': %id, 'to_id': %id}, ...],
                ...
            },
            updates: {
                created: {
                    class_name: [ %json_obj, ...],
                    ...
                },
                updated: {
                    class_name: [ %json_obj, ...],
                    ...
                },
                deleted: {
                    class_name: [ %json_obj, ...],
                    ...
                }
            }
        }
        :param progress_bar:
        :return:
        """

        def creating_new_items(item_data: Dict, class_: Type[_DBTrackedObject]):
            """
            Создает новый элент класса class_ на основании данных item_data

            :param item_data: словарь {%название_поля% : %значение_поля%,  ...}
            :param class_: класс мапппер orm sqlalchemy
            """
            if class_ == Visitation:
                item = class_.get(
                    session=session,
                    student_id=item_data['student_id'],
                    lesson_id=item_data['lesson_id'],
                    id=item_data['id']
                )
            else:
                item = class_.get(session, id=item_data['id'])
            if item is None:
                created = {key: value
                           for key, value in item_data.items()
                           if not None_or_empty(value)}
                class_.new(session, **created)
                logging.getLogger('synch').debug(f'save new: {created}')
                session.flush()

            progress_bar.increment()

        def update_existing_rows(item_data: Dict, class_: Type[_DBTrackedObject]):
            """
            Обновляет данные элемента класса class_ на основании данных item_data

            :param item_data: словарь {%название_поля% : %значение_поля%,  ...}
            :param class_: класс мапппер orm sqlalchemy
            """
            item = class_.get(session, id=item_data['id'])
            if item is None:
                creating_new_items(item_data, class_)
                return
            logging.getLogger("synch").info(f'item updated: {item}')
            for key in item_data:
                if getattr(item, key) != item_data[key]:
                    setattr(item, key, item_data[key])
                    logging.getLogger("synch").debug(f'key:{key} changed value to {item_data[key]}')

            progress_bar.increment()

        def delete_item(item_data: Dict, class_: Type[_DBTrackedObject]):
            """
            Удаляет элент класса class_ на основании данных item_data

            :param item_data: словарь {%название_поля% : %значение_поля%,  ...}
            :param class_: класс мапппер orm sqlalchemy
            """
            item: _DBTrackedObject = class_.get(session, id=item_data['id'])
            item.delete()

            progress_bar.increment()

        def change_id_to_temp(change_id: ChangeId, class_: Type[_DBTrackedObject]):
            item = class_.get(session, id=change_id.from_id)
            item.id = item.id * (-1)
            change_id.from_id = item.id
            logging.getLogger("synch").debug(f'changed {item} id to temp {item.id}')
            progress_bar.increment()

        def change_id_to_global(change_id: ChangeId, class_: Type[_DBTrackedObject]):
            item = class_.get(session, id=change_id.from_id)
            item.id = change_id.to_id
            logging.getLogger("synch").debug(f'changed {item} id to global id={change_id}')

            progress_bar.increment()

        def delay_skipped(item_data: Dict[str, Any], class_: Type[_DBTrackedObject]):
            item = class_.get(session, id=item_data['id'])
            if item is not None:
                item._updated = datetime.now()
            else:
                print('неопределённый элемент', class_, item_data)

        PART_SIZE = progress_bar.last() / 4

        session = self.professor.session()
        data = ServerUpdateData(**data)

        # Обновление id
        length = len(data.changed_id)
        progress_bar.set_part(PART_SIZE, length * 2, "Синхронизация созданных данных")
        data.changed_id.foreach(change_id_to_temp)  # присвоение времнных ID
        session.commit()
        data.changed_id.foreach(change_id_to_global)  # присвоение реальных ID

        # загрузка новых записей
        progress_bar.set_part(PART_SIZE, len(data.updates.created), "Загрузка полученных данных")
        data.updates.created.foreach(creating_new_items)
        session.flush()

        # применение изменений записей
        progress_bar.set_part(PART_SIZE, len(data.updates.updated), "Принятие изменений")
        data.updates.updated.foreach(update_existing_rows)
        session.flush()

        # применение удалений
        progress_bar.set_part(PART_SIZE, len(data.updates.deleted), "Удаление записей")
        data.updates.deleted.foreach(delete_item)
        session.flush()

        # TODO разобраться с пропускамемыми записями
        data.skiped.foreach(delay_skipped)

        session.commit()

        # обновление дат преподавтеля
        self.professor._last_update_in = datetime.now()
        self.professor._last_update_out = datetime.now()

        session.commit()
