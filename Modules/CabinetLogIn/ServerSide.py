import _md5
import random

from DataBase.Authentication import Authentication
from Modules import Module
from Modules.CabinetLogIn import address
from Server import Response


class CabinetLogInModule(Module):
    def __init__(self, app, request, db):
        super().__init__(app, request, db, address)

    def post(self, data, response: Response, auth: Authentication, **kwargs):
        uid = self.new_uid()
        self.db.set_session(uid=uid, account_id=auth.account_id)
        response.set_data(
            {
                "uid": uid,
                "page": '/cabinet'
            }
        )

    def new_uid(self):
        """

        :return: new unique session id
        """
        number = (random.random() * 100000000000000000) % 13082761331670031
        value = _md5.md5(str(number).encode()).hexdigest()
        while not self.db.free_uid(value):
            number = (random.random() * 100000000000000000) % 13082761331670031
            value = _md5.md5(str(number).encode()).hexdigest()
        return value
