from datetime import datetime
from typing import Type, Dict

from DataBase2 import Session, _DBObject, Auth, Professor
from Domain.Structures.DictWrapper.Network.FirstLoad import ServerFirstLoadData, ClientFirstLoadData
from Domain.Validation.Dict import Map
from Modules.Client import ClientWorker
from Modules.FirstLoad import address


class InitialDataLoader(ClientWorker):
    def __init__(self, login, password, host):
        super().__init__()
        self.data = {
            'user': {
                'login': login,
                'password': password
            },
            'data': ClientFirstLoadData(login=login, password=password)}
        self.address = host + address

    def on_response(self, received_data: Dict, progress_bar):
        def create_row(item_data: Dict, class_: Type[_DBObject]):
            if not class_.get(session, **item_data):
                class_.new(session, **item_data)
                session.flush()
            progress_bar.increment()

        session = Session()
        received_data = ServerFirstLoadData(**received_data)

        TOTAL_LENGTH = progress_bar.last()
        progress_bar.set_part(TOTAL_LENGTH, len(received_data.data), "Загрузка данных")

        received_data.data.foreach(create_row)

        Auth.new(session, **received_data.auth)
        professor = Professor.new(session, **Map.item_type(received_data.professor[0], Professor))
        professor._last_update_in = datetime.now()
        professor._last_update_out = datetime.now()

        session.commit()
