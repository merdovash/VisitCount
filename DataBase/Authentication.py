from DataBase.sql_handler import DataBaseWorker
from config2 import DataBaseConfig


class Authentication:
    class Status(int):
        Complete = 1
        Fail = 0

    def __init__(self, db: DataBaseWorker, config: DataBaseConfig, login=None, password=None, card_id=None, uid=None):
        self.db = db
        if (password and (card_id or login)) or uid is not None:
            if password is not None:
                if login is not None:
                    t = db.sql_request("SELECT user_id, user_type FROM {} WHERE login='{}' AND password='{}'", config.auth,
                                       login, password)
                else:
                    t = db.sql_request("""
                    SELECT user_id, user_type FROM {0} 
                    JOIN {1} ON {0}.user_id={1}.id AND {0}.user_type=1 
                    WHERE {1}.card_id='{2}' AND password='{3}'""",
                                       config.auth,
                                       config.professors,
                                       card_id,
                                       password)
            else:
                t = db.sql_request("SELECT user_id, user_type FROM {0} WHERE uid='{1}'", config.auth, uid)

            if len(t) > 0:
                self.status = Authentication.Status.Complete
                self.user_id = t[0][0]
                self.user_type = t[0][1]
            else:
                self.error = db.last_error()
                self.status = Authentication.Status.Fail
        else:
            self.error = db.last_error()
            self.status = Authentication.Status.Fail

    def get_user_info(self):
        if self.status == Authentication.Status.Complete:
            if self.user_type == 0:
                return self.db.get_students(student_id=self.user_id)[0]
            elif self.user_type == 1:
                return self.db.get_professors(professor_id=self.user_id)[0]
        else:
            return None
