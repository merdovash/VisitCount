from collections import defaultdict
from typing import Dict, Type

from DataBase2 import Auth, Professor, _DBTrackedObject, Administration
from Domain.Structures.DictWrapper.Network.Synch import ClientUpdateData, Changes, ServerUpdateData
from Modules import Module
from Modules.Synch import address
from Server.Response import Response


class SynchModule(Module):
    def __init__(self, app, request):
        super().__init__(app, request, address)

    def post(self, data: dict, response: Response, auth: Auth, **kwargs):
        """
        Находит все обновления для преподавателя


        :param data:
        :param response:
        :param auth:
        :param kwargs:
        :return:
        """

        def apply_new_item(item_data: Dict, class_: Type[_DBTrackedObject]):
            """
            Создает новый объект класса class_ на основании данных item_data

            :param item_data: словарь {%название_поля% : %значение_поля%,  ...}
            :param class_: класс мапппер orm sqlalchemy
            """
            changes = {'from_id': item_data.pop('id')}
            fields = {key: class_.column_type(key)(value) for key, value in item_data.items() if
                      key[0] != '_'}

            item = class_.get(session, **fields)
            if item is None:
                item = class_.new(session=session, **item_data)

            changes['to_id'] = item

            changed[class_.__name__].append(changes)

            session.flush()

        def apply_update(item_data: Dict, class_: Type[_DBTrackedObject]):
            """
            Обновляет данные эленты класса class_ на основании данных item_data

            :param item_data: словарь {%название_поля% : %значение_поля%,  ...}
            :param class_: класс мапппер orm sqlalchemy
            """
            item: _DBTrackedObject = class_.get(session, id=item_data['id'])
            if not item._updated or item._updated < item_data['_updated']:
                for key in item_data.keys():
                    current_value = getattr(item, key)
                    received_value = item_data[key]
                    if current_value != received_value:
                        setattr(item, key, item_data[key])
                    setattr(item, '_updated', item_data['_updated'])
                session.flush()

        def delete_item(item_data, class_: Type[_DBTrackedObject]):
            """
            Удаляет элент класса class_ на основании данных item_data

            :param item_data: словарь {%название_поля% : %значение_поля%,  ...}
            :param class_: класс мапппер orm sqlalchemy
            """
            item: _DBTrackedObject = class_.get(session, id=item_data['id'])
            item.delete()
            session.flush()

        professor: Professor = auth.user
        session = professor.session()

        received_updates = ClientUpdateData(**data)
        server_updates = Changes(**professor.updates(last_in=received_updates.last_update_in))

        # сохраняем новые записи
        changed = defaultdict(list)
        received_updates.updates.created.foreach(apply_new_item)
        session.commit()
        changed = {
            key: [
                {'from_id': i['from_id'], 'to_id': i['to_id'].id}
                for i in item
                if int(i['from_id']) != int(i['to_id'].id)
            ]
            for key, item in changed.items()
        }

        # применяем изменения записей
        received_updates.updates.updated.foreach(apply_update)
        session.commit()

        # удаляем записи
        received_updates.updates.deleted.foreach(delete_item)
        session.commit()

        # формируем ответ клиенту
        response.set_data(ServerUpdateData(changed_id=changed, updates=server_updates))
