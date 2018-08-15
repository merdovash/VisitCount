"""
    sql_handler.py
"""
from datetime import datetime
from typing import Dict, List

not_selected = "not selected"


class Logger:
    """
        log
    """

    @staticmethod
    def write(s: str) -> None:
        """

        :param s: string, value to write
        """
        logger = open("logger.txt", "a+")
        logger.write(str(s) + "\n")
        logger.close()


class DataBase:
    """
    Base class of sqlDataBase wrapper
    """

    def __init__(self, config=None):
        if config is not None:
            self.config = config
        else:
            from config2 import DataBaseConfig
            self.config = DataBaseConfig()

        self.connection = self.connect()

        self._last_error = ""

    def last_error(self):
        """

        :return: last sql error
        """
        return self._last_error

    def connect(self):
        """
        connects to database
        :return: sql connection
        """

        def _connect():
            if self.config.db == "mysql":
                import MySQLdb
                self.connection = MySQLdb.connect(host=self.config.db_host,
                                                  user=self.config.db_user,
                                                  passwd=self.config.db_password,
                                                  db=self.config.db_name,
                                                  use_unicode=True,
                                                  charset='utf8')
            elif self.config.db == "sqlite":
                import sqlite3 as sqlite
                self.connection = sqlite.connect(self.config.database_path)

        _connect()
        return self.connection

    def sql_request(self, msg, *args) -> list:
        """

        :rtype: list
        :param msg Содержит шаблон строки запроса
        :param args: Аргументы для форматирования запроса
        :return: Возвращает результат SQL запроса
        """
        message = msg.replace('\t', '').replace("  ", " ")
        arg = valid(*args)

        connection = self.connect()
        cursor = connection.cursor()
        try:
            sql = message.format(*arg)
            Logger.write(sql)
            if self.config.print:
                print(sql)
            cursor.execute(sql)
            self.connection.commit()
        except IndexError:
            Logger.write('index out of range {0} in {1}'.format(arg, message))
            self._last_error = 'internal error @ request syntax'
        except Exception as e:
            self._last_error = f'internal error @ {e}'

        temp = cursor.fetchall()
        if self.config.print:
            print(temp)
        return temp


class DataBaseWorker(DataBase):
    """
    class
    """

    def is_login_exist(self, login_name):
        """

        Check whether login is already exist or not.

        :param login_name: login
        :return: bool
        """
        res = self.sql_request("SELECT COUNT(login) FROM {0} WHERE login='{1}'",
                               self.config.auth,
                               login_name)

        if len(res) == 0:
            return False
        return True

    def create_account(self, login, password, account_type=None, user_id=None):
        # TODO: hash function to password
        """

        Creates new account by inserting new line into sql table.

        :param login: login of new user
        :param password: password of new user
        :param account_type: type of new account [0:student, 1:professor]
        :param user_id: ID of student or professor
        """
        if account_type is None:
            account_type = 0
        if user_id is None:
            user_id = 0
        self.sql_request("INSERT INTO {} (login,password,user_type,user_id) VALUES  ('{}','{}',{},{})",
                         self.config.auth,
                         login,
                         password, account_type, user_id)

    def auth(self, login=None, password=None, uid=None, card_id=None):
        # TODO: hash to function password
        """

        Process of authentication

        :param card_id: you can auth with card id + password
        :param login: login of user
        :param password: password of user
        :param uid: session ID
        :return: bool
        """
        if (login is not None or card_id is not None) and password is not None:
            if login is not None:
                res = self.sql_request("SELECT id, user_type, user_id FROM {0} WHERE login='{1}' AND password='{2}';",
                                       self.config.auth,
                                       login,
                                       password)
                if len(res) > 0:
                    return {"id": res[0][0],
                            "user_type": res[0][1],
                            "user_id": res[0][2]}
                else:
                    return False
            elif card_id is not None:
                res = self.sql_request("SELECT id FROM {0} WHERE card_id='{1}' AND password='{2}';",
                                       self.config.auth,
                                       card_id,
                                       password)
                if len(res) > 0:
                    return {"id": res[0][0]}
                else:
                    return False

        elif uid is not None:
            res = self.sql_request("SELECT user_type, user_id, id FROM {0} WHERE uid='{1}';",
                                   self.config.auth,
                                   uid)
            if len(res) > 0:
                return {"type": res[0][0],
                        "user_id": res[0][1],
                        "id": res[0][2]}
            else:
                return False

    def get_students_groups(self, professor_id=None) -> object:
        """

        :param professor_id: ID of professor
        :return: data of table students_groups
        """
        request = "SELECT DISTINCT {0}.student_id, {0}.group_id FROM {0} "
        params = [self.config.students_groups]

        if professor_id is not None:
            request += "JOIN {1} ON {1}.group_id={0}.group_id " \
                       "WHERE {1}.professor_id={2} "
            params.extend([self.config.lessons, professor_id])

            res = self.sql_request(request, *tuple(params))
            return [{'student_id': str(res[i][0]), 'group_id': str(res[i][1])} for i in range(len(res))]
        else:
            return None

    def get_auth_info(self, professor_id: int or str) -> object:
        req = "SELECT login, password, card_id, user_id, user_type FROM {0} WHERE user_type=1 AND user_id={1}"
        params = [self.config.auth, professor_id]
        res = [{"login": i[0],
                "password": i[1],
                "card_id": i[2],
                "user_id": i[3],
                "user_type": i[4]} for i in self.sql_request(req, *tuple(params))]
        return res

    def get_data_for_client(self, professor_id) -> Dict[str, List[Dict[str, str or int]]]:
        """

        :param professor_id: returns data for professor by his id
        :return: complete data for client for first connection
        """

        return {
            self.config.professors: self.get_professors(professor_id=professor_id),
            self.config.disciplines: self.get_disciplines(professor_id=professor_id),
            self.config.lessons: self.get_lessons(professor_id=professor_id),
            self.config.groups: self.get_groups(professor_id=professor_id),
            self.config.students: self.get_students(professor_id=professor_id),
            self.config.students_groups: self.get_students_groups(professor_id=professor_id),
            self.config.visitation: self.get_visitations(professor_id=professor_id),
            self.config.auth: self.get_auth_info(professor_id)
        }

    def free_uid(self, value) -> bool:
        """

        Check whether session ID is free to set to new session.

        :param value: session ID
        :return: bool
        """
        res = self.sql_request("SELECT * FROM {} "
                               "WHERE uid='{}'",
                               self.config.auth,
                               value)
        return len(res) == 0

    def set_session(self, uid: str, account_id: int or str):
        """

        Set session id to some account

        :param uid: free session ID
        :param account_id: account ID
        """
        Logger.write("before: " + str(self.sql_request("SELECT * FROM auth5 WHERE id={};", int(account_id))[0]))
        t = self.sql_request("""
            UPDATE {0}
            SET uid='{1}'
            WHERE id={2}
        """,
                             self.config.auth,
                             uid,
                             account_id)
        Logger.write("update uid, row count=" + str(t) + " || " + str(
            self.sql_request("SELECT * FROM auth5 WHERE id={};", int(account_id))[0]))

    def synchronize(self, data: list) -> tuple:
        """

        :param data: data of visitations
        :return: status of synchronisation
        """
        lessons = []
        print(data)
        try:
            if self.config.db == "sqlite":
                req = "INSERT OR IGNORE {0} (id, student_id) Values ('{1}', '{2}');"
            elif self.config.db == "mysql":
                req = "INSERT IGNORE {0} (id, student_id) VALUES ('{1}', '{2}');"
            for visit in data:
                self.sql_request(req,
                                 self.config.visitation,
                                 visit["id"],
                                 visit["student_id"])
                if visit["id"] not in lessons:
                    lessons.append(visit["id"])
                    self.sql_request("UPDATE {0} SET complete=True WHERE id={1}",
                                     self.config.lessons,
                                     visit["id"])
            return True, "OK"
        except Exception as e:
            return False, e

    def get_telegram_temp(self, code=None, account_id=None):
        request = "SELECT code, account_id FROM {0} "
        params = [self.config.telegram_temp]
        if code is not None:
            request += and_or_where(params, 1) + "code={" + str(len(params)) + "} "
            params.append(code)
        if account_id is not None:
            request += and_or_where(params, 1) + "account_id={" + str(len(params)) + "} "
            params.append(account_id)
        return [{
            "code": i[0],
            "accout_id": i[1]
        } for i in self.sql_request(request, *tuple(params))]

    def set_telegram_temp(self, account_id, code):
        request = "INSERT INTO {0} (account_id, code) VALUES ({1}, {2})"
        params = [self.config.telegram_temp, account_id, code]
        return self.sql_request(request, *tuple(params))

    def get_parent(self, student_id=None) -> dict:
        """

        :param student_id: students ID of parent's child
        :return: dictionary of full parent information
        """
        request = "SELECT email, first_name, last_name, middle_name FROM {0} " \
                  "JOIN {1} ON {0}.id={1}.parent_id " \
                  "WHERE {1}.student_id={2}"
        params = [self.config.parents,
                  self.config.parents_students,
                  student_id]
        res = self.sql_request(request, *tuple(params))
        if len(res) == 0:
            raise Exception("Parent for student <student_id={}> is not registered".format(student_id))
        return {"email": res[0][0],
                "name": "{} {} {}".format(res[0][1], res[0][2], res[0][3])}

    def setParam(self, request: str, params: list, param, string: str, size: int):
        if param is not None:
            request += and_or_where(params, size)
            request += string
            params.append(param)
        return request, params

    def get_professors(self, professor_id=None, card_id=None, group_id=None, discipline_id=None,
                       student_id=None) -> list:
        """

        :param student_id: you select professors by student
        :param discipline_id: you can select professors by discipline
        :param group_id: you can select professors by  group
        :param card_id: you can select professor by card id
        :param professor_id: you can select professor by id
        :return: Last Name, First Name, Middle Name as Dictionary
        """

        request = "SELECT {0}.first_name, {0}.last_name, {0}.middle_name, {0}.id, {0}.card_id FROM {0} "
        params = [self.config.professors]
        if group_id is not None or discipline_id is not None or student_id is not None:
            request += "JOIN {1} ON {0}.id={1}.professor_id "
            params.append(self.config.lessons)
            if student_id is not None:
                request += "JOIN {2} ON {1}.group_id={2}.group_id "
                params.append(self.config.students_groups)
                request += and_or_where(params, 3)
                request += "{2}.student_id={" + str(len(params)) + "} "
            request, params = self.setParam(request, params, group_id, "{1}.group_id={" + str(len(params)) + "} ", 2)
            request, params = self.setParam(request, params, discipline_id,
                                            "{1}.discipline_id={" + str(len(params)) + "} ", 2)
        request, params = self.setParam(request, params, professor_id, "{0}.id={" + str(len(params)) + "} ", 1)
        request, params = self.setParam(request, params, card_id, "{0}.card_id={" + str(len(params)) + "} ", 1)

        return [
            {
                "first_name": res[1],
                "last_name": res[0],
                "middle_name": res[2],
                "id": str(res[3]),
                "card_id": str(res[4])
            }
            for res in self.sql_request(request, *tuple(params))
        ]

    def get_student_name(self, student_id: int or str) -> str:
        """

        :param student_id: student ID
        :return: Full name of student as a String
        """
        res = self.get_students(student_id=student_id)
        return res[0]["last_name"] + " " + res[0]["first_name"] + " " + res[0]["middle_name"]

    def get_groups(self, professor_id=None, discipline_id=None, student_id=None, group_id=None) -> list:
        """

        :param group_id: you can select groups by id
        :param student_id: you can select groups by student
        :param professor_id: you can select groups by professor
        :param discipline_id: you can select groups by discipline
        :return: data of {"name": res[i][name], "id": res[i][id]}
        """
        request = "SELECT DISTINCT {0}.id, {0}.name FROM {0} "
        params = [self.config.groups]

        if professor_id is not None or discipline_id is not None or student_id is not None:
            request += "JOIN {1} ON {1}.group_id={0}.id "
            params.append(self.config.lessons)
            if student_id is not None:
                request += "JOIN {2} ON {2}.group_id ={1}.group_id "
                params.append(self.config.students_groups)
                request += and_or_where(params, 2)
                request += "{2}.student_id={" + str(len(params)) + "} "
                params.append(student_id)
            request, params = self.setParam(request, params, professor_id,
                                            "{1}.professor_id={" + str(len(params)) + "} ", 2)
            request, params = self.setParam(request, params, discipline_id,
                                            "{1}.discipline_id={" + str(len(params)) + "} ", 2)
        request, params = self.setParam(request, params, group_id, "{0}.id={" + str(len(params)) + "}", 2)

        return [
            {
                "name": res[1],
                "id": str(res[0])
            }
            for res in self.sql_request(request, *tuple(params))
        ]

    def get_disciplines(self, student_id=None, professor_id=None, discipline_id=None, group_id=None) -> list:
        """

        :param group_id: you can select disciplines by group
        :param discipline_id: you can select disciplines by id
        :param professor_id: you can select disciplines by professor
        :param student_id: you can select disciplines by student
        :return: data of disciplines
        """

        request = "SELECT DISTINCT {0}.id, {0}.name FROM {0} " \
                  "JOIN {1} ON {0}.id={1}.discipline_id "
        params = [self.config.disciplines, self.config.lessons]
        if student_id is not None:
            request += "JOIN {2} ON {1}.group_id={2}.group_id " \
                       "WHERE {2}.student_id={3}"
            params.extend([self.config.students_groups, student_id])
        request, params = self.setParam(request, params, professor_id, "{1}.professor_id={" + str(len(params)) + "} ",
                                        2)
        request, params = self.setParam(request, params, discipline_id, "{0}.id={" + str(len(params)) + "} ", 2)
        request, params = self.setParam(request, params, group_id, "{1}.group_id={" + str(len(params)) + "} ", 2)

        return [
            {
                "name": res[1],
                "id": str(res[0])
            }
            for res in self.sql_request(request, *tuple(params))
        ]

    def get_students(self, group_id=None, student_list=None, professor_id=None, student_id=None, card_id=None) -> list:
        """

        :param student_id: you can select students by id
        :param group_id: you can select students by group
        :param student_list: you can select students by data if id
        :param professor_id: you can select students by professor
        :return: data of students  keys=(id, last_name, first_name, middle_name, card_id)
        """
        request = "SELECT DISTINCT {0}.id, {0}.first_name, {0}.last_name, {0}.middle_name, {0}.card_id " \
                  "FROM {0} "
        params = [self.config.students]

        if group_id is not None or professor_id is not None:
            request += "JOIN {1} ON {1}.student_id={0}.id " \
                       "JOIN {2} ON {2}.group_id={1}.group_id "
            params.extend([self.config.students_groups, self.config.lessons])
            request, params = self.setParam(request, params, professor_id,
                                            "{2}.professor_id={" + str(len(params)) + "} ", 3)
            request, params = self.setParam(request, params, group_id, "{1}.group_id={" + str(len(params)) + "} ", 3)
        request, params = self.setParam(request, params, student_list, "{0}.id IN {" + str(len(params)) + "} ", 1)
        request, params = self.setParam(request, params, student_id, "{0}.id={" + str(len(params)) + "} ", 1)
        request, params = self.setParam(request, params, card_id, "{0}.card_id={" + str(len(params)) + "} ", 1)

        return [{"id": str(res[0]),
                 "last_name": res[2],
                 "first_name": res[1],
                 "middle_name": res[3],
                 "card_id": str(res[4])
                 } for res in self.sql_request(request, *tuple(params))]

    def get_lessons(self, group_id=None, professor_id=None, discipline_id=None, student_id=None,
                    lesson_id=None) -> list:
        """

        :param lesson_id: you can select lessons by id
        :param student_id: you can select lessons by student
        :param group_id: you can select lessons by group
        :param professor_id: you can select lessons by professor
        :param discipline_id: you can select lessons by discipline
        :return: data of lessons
        """
        request = "SELECT DISTINCT {0}.id, {0}.date, {0}.room_id, {0}.group_id, {0}.discipline_id, {0}.professor_id," \
                  " {0}.completed, {0}.type FROM {0} "
        params = [self.config.lessons]
        if student_id is not None:
            request += "JOIN {1} ON {0}.group_id={1}.group_id "
            params.append(self.config.students_groups)
            request += and_or_where(params, 2)
            request += "{1}.student_id={" + str(len(params)) + "} "
            params.append(student_id)
        request, params = self.setParam(request, params, group_id, "{0}.group_id={" + str(len(params)) + "} ", 1)
        request, params = self.setParam(request, params, professor_id, "{0}.professor_id={" + str(len(params)) + "} ",
                                        1)
        request, params = self.setParam(request, params, discipline_id, "{0}.discipline_id={" + str(len(params)) + "} ",
                                        1)
        request, params = self.setParam(request, params, lesson_id, "{0}.id={" + str(len(params)) + "} ", 1)

        request += "ORDER BY {0}.date "

        return [{'id': str(res[0]),
                 'date': str(res[1]),
                 'room_id': str(res[2]),
                 'group_id': str(res[3]),
                 'discipline_id': str(res[4]),
                 'professor_id': str(res[5]),
                 'type': str(res[7]),
                 'completed': res[6]
                 } for res in self.sql_request(request, *tuple(params))]

    def get_visitations(self, group_id=None, professor_id=None, discipline_id=None, student_list=None,
                        student_id=None, synch=None) -> list:
        """

        :param synch: you can select visitation by synch status
        :param student_id: you can select visitations by student
        :param group_id: you can select visitations by group
        :param professor_id: you can select visitations by professor
        :param discipline_id: you can select visitations by discipline
        :param student_list: you can select visitations by student data
        :return:
        """
        request = "SELECT DISTINCT {0}.student_id, {0}.lesson_id FROM {0} "
        params = [self.config.visitation]
        request += "JOIN {1} ON {0}.lesson_id={1}.id "
        params.append(self.config.lessons)
        if student_list is not None or student_id is not None:
            if student_list is not None:
                request += "WHERE {0}.student_id IN ({" + str(len(params)) + "}) "
                params.extend(student_list)
            else:
                request += "WHERE {0}.student_id={" + str(len(params)) + "} "
                params.append(student_id)
        request, params = self.setParam(request, params, group_id, "{1}.group_id={" + str(len(params)) + "} ", 2)
        request, params = self.setParam(request, params, professor_id, "{1}.professor_id={" + str(len(params)) + "} ",
                                        2)
        request, params = self.setParam(request, params, discipline_id, "{1}.discipline_id={" + str(len(params)) + "} ",
                                        2)
        request, params = self.setParam(request, params, synch, "{0}.synch={" + str(len(params)) + "}", 2)

        return [{
            "student_id": str(res[0]),
            "id": str(res[1])
        }
            for res in self.sql_request(request, *tuple(params))]

    def get_table(self, student_id=None, professor_id=None, discipline_id=None, group_id=None, user_type=None):
        if user_type is None:
            request = """
            SELECT
                {0}.date,
                CASE lessons.complete
                    WHEN 1 THEN {2}.student_id
                    WHEN 0 THEN -1
                END
            FROM {0}
            JOIN {1} ON {1}.group_id={0}.group_id
            LEFT JOIN {2} ON {2}.student_id={1}.student_id AND {0}.id={2}.lesson_id
            """
            params = [self.config.lessons, self.config.students_groups, self.config.visitation]
            if student_id is not None:
                request += and_or_where(params, 3) + "{1}.student_id={" + str(len(params)) + "} "
                params.append(student_id)
            if professor_id is not None:
                request += and_or_where(params, 3) + "{0}.professor_id={" + str(len(params)) + "} "
                params.append(professor_id)
            if group_id is not None:
                request += and_or_where(params, 3) + "{0}.group_id={" + str(len(params)) + "} "
                params.append(group_id)
            if discipline_id is not None:
                request += and_or_where(params, 3) + "{0}.discipline_id={" + str(len(params)) + "} "
                params.append(discipline_id)
            request += "ORDER BY {0}.date; "
            print(self.sql_request(request, *tuple(params)))
            return [
                {
                    "student_id": "-1" if str(i[1]) == "-1" else ("1" if str(i[1]) == str(student_id) else "0")
                } for i in self.sql_request(request, *tuple(params))
            ]
        elif str(user_type) == "1":
            return {
                "lessons": [[lesson["date"], lesson["type"]] for lesson in
                            self.get_lessons(professor_id=professor_id, group_id=group_id,
                                             discipline_id=discipline_id)],
                "students": [{
                    "first_name": student["first_name"],
                    "last_name": student["last_name"],
                    "middle_name": student["middle_name"],
                    "visitations": [c["student_id"] for c in
                                    self.get_table(student_id=student["id"], discipline_id=discipline_id,
                                                   professor_id=professor_id, group_id=group_id)]
                } for student in self.get_students(group_id=group_id)
                ]
            }
        elif str(user_type) == "0":
            return {
                "lessons": [[lesson["date"], lesson["type"]] for lesson in self.get_lessons(student_id=student_id,
                                                                                            discipline_id=discipline_id,
                                                                                            group_id=(self.get_groups(
                                                                                                student_id=student_id)[
                                                                                                          0]["id"])
                                                                                            )],
                "students": [{
                    "first_name": student["first_name"],
                    "last_name": student["last_name"],
                    "middle_name": student["middle_name"],
                    "visitations": [c["student_id"] for c in
                                    self.get_table(student_id=student_id, discipline_id=discipline_id,
                                                   group_id=self.get_groups(student_id=student_id)[0]["id"])]
                } for student in self.get_students(student_id=student_id)
                ]
            }
        else:
            return False

    def get_total(self, admin_id=None, user_type=None):
        if str(user_type) == "2":
            request = """
                SELECT
                    {2}.id,
                    count(distinct {4}.id, {4}.student_id)/(count({3}.id))*100 AS 'ctn',
                    {2}.name
                FROM {0}
                JOIN {1} ON {0}.id={1}.student_id
                JOIN {2} ON {1}.group_id={2}.id
                JOIN {3} ON {2}.id={3}.group_id
                LEFT JOIN {4} ON {3}.id={4}.lesson_id AND {0}.id={4}.student_id
                GROUP BY {2}.id
            """
            params = [
                self.config.students,
                self.config.students_groups,
                self.config.groups,
                self.config.lessons,
                self.config.visitation]
            return [{
                "id": i[0],
                "%": float(i[1]),
                "name": str(i[2])
            } for i in self.sql_request(request, *tuple(params))]
        else:
            return []

    def get_groups_of_total(self, group_id: int, admin_id=None, user_type=None):
        """
        return total visitation of student of selected group
        :param group_id: ID of group
        :param admin_id: ID of user
        :param user_type: type of user
        """
        if str(user_type) == "2":
            request = """
            SELECT
                {0}.id,
                {0}.last_name,
                {0}.first_name,
                {0}.middle_name,
                COUNT(distinct {3}.lesson_id, {3}.student_id)/(count(distinct {2}.id))*100 as '%'
            FROM {0}
            JOIN {1} on {0}.id={1}.student_id
            JOIN {2} on {1}.group_id={2}.group_id
            LEFT JOIN {3} on {2}.id={3}.lesson_id and {0}.id={3}.student_id
            WHERE {1}.group_id={4}
            GROUP BY {0}.id
            ORDER BY '%'
            """
            params = [
                self.config.students,
                self.config.students_groups,
                self.config.lessons,
                self.config.visitation,
                group_id]

            return [{
                "id": i[0],
                "last_name": i[1],
                "first_name": i[2],
                "middle_name": i[3],
                "%": float(i[4])
            } for i in self.sql_request(request, *tuple(params))]
        return []

    def get_the_lessons_count(self, student_id: int or str, discipline_id: int or str) -> int:
        """

        :param student_id: ID of student
        :param discipline_id: ID of discipline
        :return: number of completed lessons
        """
        return self.sql_request("SELECT COUNT(DISTINCT id) FROM {0} "
                                "JOIN {1} ON {1}.group_id={0}.group_id "
                                "WHERE {1}.student_id={2} AND {0}.discipline_id={3}",
                                self.config.lessons,
                                self.config.students_groups,
                                student_id,
                                discipline_id)[0][0]

    def get_visited_lessons_count(self, student_id: int or str, discipline_id: int or str) -> int:
        """

        :param student_id: ID of student
        :param discipline_id: ID of discipline
        :return: number of visited lessons
        """
        return self.sql_request("SELECT COUNT(DISTINCT {0}.id) FROM {0} "
                                "JOIN {1} ON {1}.id={0}.id "
                                "JOIN {2} ON {1}.group_id={2}.group_id "
                                "WHERE {2}.student_id={3} AND {1}.discipline_id={4}",
                                self.config.visitation,
                                self.config.lessons,
                                self.config.students_groups,
                                student_id,
                                discipline_id)[0][0]

    def get_notification_params(self, professor_id=None, discipline_id=None, group_id=None) -> list:
        """

        :param professor_id: you can select notification params by professor
        :param discipline_id: you can select notification params by discipline
        :param group_id: you can select notification params by group
        :return: data of {"professor_id": str, "group_id": str, "discipline_id": str, "max_loss": str}
        """
        request = "SELECT "
        if professor_id is None:
            request += "professor_id "
        if group_id is None:
            if len(request) > 7:
                request += ", "
            request += "group_id "
        if discipline_id is None:
            if len(request) > 7:
                request += ", "
            request += "discipline_id "
        if len(request) > 7:
            request += ", "
        request += "max_loss FROM {0} "
        params = [self.config.notification_params]
        if professor_id is not None or discipline_id is not None or group_id is not None:
            request += "WHERE "
            if professor_id is not None:
                request += and_or_where(params, 1) + "professor_id={" + str(len(params)) + "} "
                params.append(professor_id)
            if group_id is not None:
                request += and_or_where(params, 1) + "group_id={" + str(len(params)) + "} "
                params.append(group_id)
            if discipline_id is not None:
                request += and_or_where(params, 1) + "discipline_id={" + str(len(params)) + "} "
                params.append(discipline_id)
        res = self.sql_request(request, *tuple(params))
        if len(res) > 0:
            return [{"professor_id": str(professor_id if professor_id is not None else res[i][0]),
                     "group_id": str(group_id if group_id is not None else res[i][1]),
                     "discipline_id": str(discipline_id if discipline_id is not None else res[i][2]),
                     "max_loss": str(res[i][3])}
                    for i in range(len(res))]

    def set_notification_params(self, new_value: int or str, professor_id=None, discipline_id=None, group_id=None):
        """

        :param new_value:
        :param professor_id:
        :param discipline_id:
        :param group_id:
        """
        request = "UPDATE {0} SET max_loss={1} "
        params = [self.config.notification_params, new_value]
        if professor_id is not None:
            request += and_or_where(params, 2)
            request += "professor_id={" + str(len(params)) + "} "
            params.append(professor_id)
        if discipline_id is not None:
            request += and_or_where(params, 2)
            request += "discipline_id={" + str(len(params)) + "} "
            params.append(discipline_id)
        if group_id is not None:
            request += and_or_where(params, 2)
            request += "group_id={" + str(len(params)) + "} "
            params.append(group_id)

        self.sql_request(request, *tuple(params))

    def get_data_for_student_table(self, student_id: int or str, group_id: int or str, discipline_id) -> dict:
        """

        :param student_id: student ID
        :param group_id: group ID
        :param discipline_id: data if disciplines
        :return: data dict
        """
        visitation = self.sql_request("SELECT DISTINCT {0}.id, {1}.discipline_id, {1}.date FROM {0} "
                                      "JOIN {1} ON {1}.id={0}.id "
                                      "WHERE {0}.student_id={2} AND {1}.group_id={3} AND {1}.discipline_id in ({4})",
                                      self.config.visitation,
                                      self.config.lessons,
                                      student_id,
                                      group_id,
                                      discipline_id
                                      )
        try:
            data = {
                "data": [{"col_id": visitation[i][0], "row_id": visitation[i][1]} for i in range(len(visitation))],
                "cols_head": {lesson["id"]: lesson["date"] for lesson in self.get_lessons(student_id=student_id)},
                "rows_head": self.get_disciplines(discipline_id=discipline_id)[0]["name"],
                "head":
                    {
                        "Группа": self.get_groups(group_id=group_id),
                        "Студент": self.get_student_name(student_id=student_id),
                        "Дисциплина": self.get_disciplines(discipline_id=discipline_id),
                        "Преподаватель": self.get_professors(group_id=group_id, discipline_id=discipline_id)[0]
                    }
            }
            return data
        except Exception as e:
            raise e

    def get_data_for_professor(self, discipline_id: int or str, group_id: int or str, professor_id: int or str,
                               student_list):
        """

        :param discipline_id:
        :param group_id:
        :param professor_id:
        :param student_list:
        :return:
        """
        discipline_id = int(discipline_id)
        group_id = int(group_id)
        professor_id = int(professor_id)
        data = {"students": self.get_students(group_id=group_id,
                                              student_list=student_list),
                "lessons": self.get_lessons(group_id=group_id, professor_id=professor_id, discipline_id=discipline_id),
                "data": self.get_visitations(group_id=group_id,
                                             professor_id=professor_id,
                                             discipline_id=discipline_id,
                                             student_list=student_list),
                "professor_name": self.get_professors(professor_id=professor_id)[0],
                "discipline_name": self.get_disciplines(discipline_id=discipline_id)[0]["name"],
                "group_name": self.get_groups(group_id=group_id)
                }
        return data

    def get_table2(self, owner, student_id=None, professor_id=None, group_id=None, discipline_id=None):
        if owner == "student":
            request = "SELECT DISTINCT {0}.date, {2}.name FROM {0} " \
                      "JOIN {1} ON {1}.id={0}.id " \
                      "JOIN {2} ON {0}.discipline_id={2}.id " \
                      "JOIN {3} ON {3}.group_id={0}.group_id " \
                      "WHERE {0}.discipline_id IN {4} AND {3}.student_id={5} " \
                      "ORDER  BY {0}.date"
            params = [self.config.lessons,
                      self.config.visitation,
                      self.config.disciplines,
                      self.config.students_groups,
                      discipline_id if discipline_id is tuple else "({})".format(discipline_id),
                      student_id]
            lessons = self.sql_request(request, *tuple(params))
            data = {}
            for v in lessons:
                if v[1] not in data:
                    data[v[1]] = {}
                data[v[1]][v[0]] = False
            request = "SELECT DISTINCT {0}.date, {2}.name FROM {0} " \
                      "JOIN {1} ON {1}.id={0}.id " \
                      "JOIN {2} ON {0}.discipline_id={2}.id " \
                      "WHERE {0}.discipline_id IN {3} AND {1}.student_id={4} "
            params = [self.config.lessons,
                      self.config.visitation,
                      self.config.disciplines,
                      discipline_id if discipline_id is tuple else "({})".format(discipline_id),
                      student_id]
            visit = self.sql_request(request, *tuple(params))
            print(visit)
            for v in visit:
                data[v[1]][v[0]] = True
        return data

    def update_student_card_id(self, student_id, card_id):
        req = "UPDATE {} SET card_id={} WHERE id={}"
        params = [self.config.students, card_id, student_id]

        res = self.sql_request(req, *tuple(params))

        self.field_updated(table=self.config.students, id=student_id)

    def field_updated(self, table, id):
        updates_list = self.sql_request("SELECT id FROM updates WHERE table_name='{0}' AND row_id={1};", table, id)
        if len(updates_list) == 0:
            req = "INSERT INTO {0} (table_name, row_id) VALUES ('{1}',{2});".format(self.config.updates, table, id)
            res = self.sql_request(req)
            update_id = self.cursor.lastrowid[0]
        else:
            update_id = updates_list[0][0]

        if table == self.config.students:
            professors_list = self.sql_request("""
            SELECT DISTINCT professor_id 
            FROM {0} 
            JOIN {1} ON {0}.group_id={1}.group_id 
            WHERE {1}.student_id={2}""",
                                               self.config.lessons,
                                               self.config.students_groups,
                                               id)
            self.sql_request("insert into {0}(update_id, professor_id) Values {1}", self.config.professors_updates,
                             ','.join(
                                 ["({}, {})".format(update_id, professor_id[0]) for professor_id in professors_list]))

    def get_updates_list(self, professor_id):

        return self.sql_request("""
        SELECT DISTINCT table_name, row_id 
        FROM {0} 
        JOIN {1} ON {0}.id={1}.update_id 
        WHERE {1}.professor_id = {2}""",
                                self.config.updates,
                                self.config.professors_updates,
                                professor_id)

    def get_updates(self, professor_id):
        updates_list = self.get_updates_list(professor_id)
        sorted_updates = {}
        for update in updates_list:
            if update[0] not in sorted_updates:
                sorted_updates[update[0]] = []
            sorted_updates[update[0]].append(update[1])
        updates = {}
        for table in sorted_updates:
            updates[table] = self.sql_request("SELECT * FROM {0} WHERE id IN ({1})", table,
                                              ",".join([str(i) for i in sorted_updates[table]]))
        return updates


def and_or_where(params, size):
    """

    :param params: data of params
    :param size: standard data size
    :return: "AND " or "WHERE "
    """
    if len(params) > size:
        return "AND "
    else:
        return "WHERE "


def remove_banned_symbols(string):
    """

    :param string: String that will be insert into sql request
    :return: String without restricted symbols
    """
    for banned_symbol in ["\'", ";", "\""]:
        string = string.split(banned_symbol)[0]
    return string


def valid(*args) -> tuple:
    """

    :rtype: tuple or str
    """
    if len(args) == 1:
        if type(args) == str:
            c = args
            return remove_banned_symbols(c)
        else:
            return args

    valid_list = []
    for val in tuple(args):
        if type(val) == str:
            valid_list.append(remove_banned_symbols(val))
        elif type(val) == int:
            valid_list.append(val)

    return tuple(valid_list)


class ClientDataBase(DataBaseWorker):
    def add_visit(self, student_id: int, lesson_id: int):
        r = self.sql_request("INSERT INTO {0}(student_id, id, synch) VALUES ({1}, {2}, {3})",
                             self.config.visitation,
                             student_id,
                             lesson_id,
                             0)
        print("new visit", student_id, lesson_id, r)
        return r

    def complete_lesson(self, lesson_id: int):
        r = self.sql_request("UPDATE {0} SET completed=1 WHERE id={1}",
                             self.config.lessons,
                             lesson_id)
        return r

    def update_lesson_date(self, lesson_id: int, new_date: datetime):
        # TODO send update on server
        r = self.sql_request("UPDATE {0} SET date='{1}' WHERE id={2}",
                             self.config.lessons,
                             new_date.strftime("%d-%m-%Y %I:%M%p"),
                             lesson_id)

    def get_auth(self, professor_id) -> list:
        req = "SELECT card_id, password FROM {0} WHERE user_id={1}"
        params = [self.config.auth, professor_id]

        res = self.sql_request(req, *tuple(params))

        return [{
            "card_id": i[0],
            "password": i[1]
        } for i in res]

    def start_lesson(self, lesson_id=None):
        req = "UPDATE {} SET completed=1 WHERE id={}"
        params = [self.config.lessons, lesson_id]

        res = self.sql_request(req, *tuple(params))

        return res

    def add_card_id_to(self, card_id: int, student_id=None):
        req = "UPDATE {} SET card_id={} WHERE id={}"
        params = [self.config.students,
                  card_id,
                  student_id]

        res = self.sql_request(req, *tuple(params))
        return res

    def update_student(self, **kwargs):
        keys = ["id", "last_name", "middle_name", "first_name", "card_id"]
        c = {}
        for key in keys:
            c[key] = kwargs.get(key, None)

        self.insert_into(self.config.students, **c)

    def insert_into(self, table, **kwargs):
        return self.sql_request("""INSERT OR UPDATE INTO {} ({}) VALUES ({});""",
                                table,
                                ','.join(kwargs.keys()),
                                ','.join([kwargs[i] for i in kwargs.keys()]))
