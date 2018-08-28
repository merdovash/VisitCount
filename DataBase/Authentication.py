from DataBase.sql_handler import DataBaseWorker


class Authentication:
    __slots__ = ('db', 'status', 'user_id', 'user_type', 'account_id', '_info', 'error')

    class Status(int):
        Complete = 1
        Fail = 0

    class UserType(int):
        Professor = 1
        Student = 0
        Parent = 3
        Administration = 2

    def __init__(self, db: DataBaseWorker, login=None, password=None, card_id=None, uid=None, **kwargs):
        self._info = None
        self.db = db
        if (password and (card_id or login)) or uid is not None:
            if password is not None:
                if login is not None:
                    t = db.sql_request("""
                    SELECT user_id, user_type, id 
                    FROM {} 
                    WHERE login='{}' AND password='{}'""",
                                       db.config.auth,
                                       login,
                                       password)
                else:
                    t = db.sql_request("""
                    SELECT user_id, user_type, id 
                    FROM {0} 
                    JOIN {1} ON {0}.user_id={1}.id AND {0}.user_type=1 
                    WHERE {1}.card_id='{2}' AND password='{3}'""",
                                       db.config.auth,
                                       db.config.professors,
                                       card_id,
                                       password)
            else:
                t = db.sql_request("SELECT user_id, user_type, id FROM {0} WHERE uid='{1}'",
                                   db.config.auth,
                                   uid)

            print(db.sql_request("SELECT * FROM {}", db.config.auth))
            if len(t) > 0:
                self.status = Authentication.Status.Complete
                self.user_id = t[0][0]
                self.user_type = Authentication.UserType(t[0][1])
                self.account_id = t[0][2]
            else:
                self.error = db.last_error()
                self.status = Authentication.Status.Fail
        else:
            self.error = db.last_error()
            self.status = Authentication.Status.Fail

    def get_user_info(self):
        if self.status == Authentication.Status.Complete:
            if self._info is None:
                if self.user_type == 0:
                    self._info = self.db.get_students(student_id=self.user_id)[0]
                elif self.user_type == 1:
                    self._info = self.db.get_professors(professor_id=self.user_id)[0]
            self._info["user_type"] = self.user_type
            return self._info
        else:
            return None
