"""
    sql_handler.py
"""
import sqlite3
import traceback
from datetime import datetime

from Main import config
import MySQLdb
import _mysql_exceptions

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
        # logger = open(config.logger, "a+")
        # logger.write(str(s) + "\n")
        # logger.close()


def setParam(request: str, params: list, param, string: str, size: int):
    if param is not None:
        request += and_or_where(params, size)
        request += string
        params.append(param)
    return request, params


class DataBaseWorker:
    """
    SINGLETON
    """
    inst = None

    @staticmethod
    def instance():
        if DataBaseWorker.inst is None:
            DataBaseWorker.inst = DataBaseWorker()
        return DataBaseWorker.inst

    def __init__(self, app=None):
        if DataBaseWorker.inst is not None:
            raise Exception("too much instances")
        self.app = app
        self.init_connection()
        self.created = None
        self.connection = None

    def init_connection(self):
        pass

    def is_login_exist(self, login_name):
        """

        Check whether login is already exist or not.

        :param login_name: login
        :return: bool
        """
        res = self.sql_request("SELECT COUNT(login) FROM {0} WHERE login='{1}'",
                               config.auth,
                               login_name)

        if len(res) == 0:
            return False
        return True

    def loads(self, table, data, marker=None):
        if config.db == "sqlite":
            types = {i[1]: i[2] for i in self.sql_request("PRAGMA table_info({0});", table)}

            def to_format(value, key):
                if types[key] == "INTEGER" or types[key] == "INT":
                    return str(value)
                else:
                    return "'" + str(value) + "'"

            req = "INSERT OR IGNORE INTO {0}({1}) VALUES {2}"
            keys = data[0].keys()
            params = [
                table,
                ', '.join(keys),
                ', '.join(
                    ['(' + ', '.join([to_format(line[key], key) for key in keys]) + ')' for line in data])
            ]
            params[2] = params[2].replace("\r", "").replace("\n", "")

            print(*tuple(params))

            res = self.sql_request(req, *tuple(params), ignore_banned_symbols=True)

        elif config.db == "mysql":
            req = "INSERT IGNORE INTO {0}({1}) VALUES {2}"
            keys = data[0].keys()
            params = [
                table,
                ', '.join(keys),
                ', '.join(
                    ['(' + ', '.join([line[key] for key in keys]) + ')' for line in data])  # TODO: to foramt function
            ]

            res = self.sql_request(req, *tuple(params))
        return res

    def load(self, table, data):
        if config.db == "sqlite":
            req = "INSERT OR IGNORE INTO {0}({1}) VALUES {2}"
            types = {i[1]: i[2] for i in self.sql_request("PRAGMA table_info({0});", table)}

            def to_format(value, key):
                if types[key] == "INTEGER":
                    return str(value)
                else:
                    return "'" + str(value) + "'"

        elif config.db == "mysql":
            req = "INSERT IGNORE INTO {0}({1}) VALUES {2}"
        keys = data.keys()
        params = [
            table,
            ', '.join(keys),
            '(' + ','.join([to_format(data[key], key) for key in keys]) + ')'
        ]

        return self.sql_request(req, *tuple(params), ignore_banned_symbols=True)

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
        self.sql_request("INSERT INTO {} (login,password,user_type,user_id) VALUES  ('{}','{}',{},{})", config.auth,
                         login,
                         password, account_type, user_id)

    class AuthStatus(int):
        Success = 1
        Fail = 0
        NoData = 2

    def auth(self, login=None, password=None, uid=None, card_id=None) -> (AuthStatus, int):
        # TODO: auth
        print(card_id)
        if card_id is not None:
            print(password)
            res = self.sql_request("Select * from {} WHERE card_id={}",
                                   config.auth,
                                   card_id)
            if len(res) == 0:
                return DataBaseWorker.AuthStatus.NoData, None
            else:
                res = self.sql_request("SELECT user_id FROM {0} WHERE card_id={1} AND password={2}",
                                       config.auth,
                                       card_id,
                                       password)
                if len(res) == 0:
                    return DataBaseWorker.AuthStatus.Fail, None
                else:
                    return DataBaseWorker.AuthStatus.Success, res[0][0]
        else:
            res = self.sql_request("SELECT user_id FROM {0} WHERE login='{1}' AND password='{2}' AND user_type=1",
                                   config.auth,
                                   login,
                                   password)
            if len(res) == 0:
                return DataBaseWorker.AuthStatus.NoData, None
            else:
                return DataBaseWorker.AuthStatus.Success, res[0][0]

    def get_students_groups(self, professor_id=None) -> object:
        """

        :param professor_id: ID of professor
        :return: data of table students_groups
        """
        request = "SELECT DISTINCT {0}.student_id, {0}.group_id FROM {0} "
        params = [config.students_groups]

        if professor_id is not None:
            request += "JOIN {1} ON {1}.group_id={0}.group_id " \
                       "WHERE {1}.professor_id={2} "
            params.extend([config.lessons, professor_id])

            res = self.sql_request(request, *tuple(params))
            return [{'student_id': str(res[i][0]), 'group_id': str(res[i][1])} for i in range(len(res))]
        else:
            return None

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
        params = [config.professors]
        if group_id is not None or discipline_id is not None or student_id is not None:
            request += "JOIN {1} ON {0}.id={1}.professor_id "
            params.append(config.lessons)
            if student_id is not None:
                request += "JOIN {2} ON {1}.group_id={2}.group_id "
                params.append(config.students_groups)
                request += and_or_where(params, 3)
                request += "{2}.student_id={" + str(len(params)) + "} "
            request, params = setParam(request, params, group_id, "{1}.group_id={" + str(len(params)) + "} ", 2)
            request, params = setParam(request, params, discipline_id,
                                       "{1}.discipline_id={" + str(len(params)) + "} ", 2)
        request, params = setParam(request, params, professor_id, "{0}.id={" + str(len(params)) + "} ", 1)
        request, params = setParam(request, params, card_id, "{0}.card_id={" + str(len(params)) + "} ", 1)

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
        params = [config.groups]

        if professor_id is not None or discipline_id is not None or student_id is not None:
            request += "JOIN {1} ON {1}.group_id={0}.id "
            params.append(config.lessons)
            if student_id is not None:
                request += "JOIN {2} ON {2}.group_id ={1}.group_id "
                params.append(config.students_groups)
                request += and_or_where(params, 2)
                request += "{2}.student_id={" + str(len(params)) + "} "
                params.append(student_id)
            request, params = setParam(request, params, professor_id,
                                       "{1}.professor_id={" + str(len(params)) + "} ", 2)
            request, params = setParam(request, params, discipline_id,
                                       "{1}.discipline_id={" + str(len(params)) + "} ", 2)
        request, params = setParam(request, params, group_id, "{0}.id={" + str(len(params)) + "}", 2)

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
        params = [config.disciplines, config.lessons]
        if student_id is not None:
            request += "JOIN {2} ON {1}.group_id={2}.group_id " \
                       "WHERE {2}.student_id={3}"
            params.extend([config.students_groups, student_id])
        request, params = setParam(request, params, professor_id, "{1}.professor_id={" + str(len(params)) + "} ",
                                   2)
        request, params = setParam(request, params, discipline_id, "{0}.id={" + str(len(params)) + "} ", 2)
        request, params = setParam(request, params, group_id, "{1}.group_id={" + str(len(params)) + "} ", 2)

        return [
            {
                "name": res[1],
                "id": str(res[0])
            }
            for res in self.sql_request(request, *tuple(params))
        ]

    def get_students(self, group_id=None, student_list=None, professor_id=None, student_id=None, discipline_id=None,
                     card_id=None) -> list:
        """

        :param discipline_id: you can select students by discipline_id
        :param card_id: you can select students by card_id
        :param student_id: you can select students by id
        :param group_id: you can select students by group
        :param student_list: you can select students by data if id
        :param professor_id: you can select students by professor
        :return: data of students  keys=(id, last_name, first_name, middle_name, card_id)
        """
        request = "SELECT DISTINCT {0}.id, {0}.first_name, {0}.last_name, {0}.middle_name, {0}.card_id " \
                  "FROM {0} "
        params = [config.students]

        if group_id is not None or professor_id is not None or discipline_id is not None:
            if group_id is not None:
                request += "JOIN {1} ON {1}.student_id={0}.id "
                params.extend([config.students_groups])
            if professor_id is not None or discipline_id is not None:
                request += "JOIN {2} ON {2}.group_id={1}.group_id "
                params.extend([config.lessons])
                if professor_id is not None:
                    request, params = setParam(request, params, professor_id,
                                               "{2}.professor_id={" + str(len(params)) + "} ", 3)
                if discipline_id is not None:
                    request, params = setParam(request, params, discipline_id,
                                               "{2}.discipline_id={" + str(len(params)) + "} ", 3)

        if group_id is not None:
            request, params = setParam(request, params, group_id, "{1}.group_id={" + str(len(params)) + "} ", 1)
        if student_list is not None:
            request, params = setParam(request, params, student_list, "{0}.id IN {" + str(len(params)) + "} ", 1)
        if student_id is not None:
            request, params = setParam(request, params, student_id, "{0}.id={" + str(len(params)) + "} ", 1)
        if card_id is not None:
            request, params = setParam(request, params, card_id, "{0}.card_id={" + str(len(params)) + "} ", 1)

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
        params = [config.lessons]
        if student_id is not None:
            request += "JOIN {1} ON {0}.group_id={1}.group_id "
            params.append(config.students_groups)
            request += and_or_where(params, 2)
            request += "{1}.student_id={" + str(len(params)) + "} "
            params.append(student_id)
        request, params = setParam(request, params, group_id, "{0}.group_id={" + str(len(params)) + "} ", 1)
        request, params = setParam(request, params, professor_id, "{0}.professor_id={" + str(len(params)) + "} ",
                                   1)
        request, params = setParam(request, params, discipline_id, "{0}.discipline_id={" + str(len(params)) + "} ",
                                   1)
        request, params = setParam(request, params, lesson_id, "{0}.id={" + str(len(params)) + "} ", 1)

        request += "ORDER BY {0}.date "

        r = [{'id': str(res[0]),
              'date': str(res[1]),
              'room': str(res[2]),
              'group_id': str(res[3]),
              'discipline_id': str(res[4]),
              'professor_id': str(res[5]),
              'type': str(res[7]),
              'completed': res[6]
              } for res in self.sql_request(request, *tuple(params))]
        return r

    def get_visitations(self, group_id=None, professor_id=None, discipline_id=None, student_list=None,
                        student_id=None, synch=None) -> list:
        """

        :param synch: you can select visitations by synch status
        :param student_id: you can select visitations by student
        :param group_id: you can select visitations by group
        :param professor_id: you can select visitations by professor
        :param discipline_id: you can select visitations by discipline
        :param student_list: you can select visitations by student data
        :return:
        """
        request = "SELECT DISTINCT {0}.student_id, {0}.lesson_id FROM {0} "
        params = [config.visitation]
        request += "JOIN {1} ON {0}.lesson_id={1}.id "
        params.append(config.lessons)
        if student_list is not None or student_id is not None:
            if student_list is not None:
                request += "WHERE {0}.student_id IN ({" + str(len(params)) + "}) "
                params.extend(student_list)
            else:
                request += "WHERE {0}.student_id={" + str(len(params)) + "} "
                params.append(student_id)
        request, params = setParam(request, params, group_id, "{1}.group_id={" + str(len(params)) + "} ", 2)
        request, params = setParam(request, params, professor_id, "{1}.professor_id={" + str(len(params)) + "} ",
                                   2)
        request, params = setParam(request, params, discipline_id, "{1}.discipline_id={" + str(len(params)) + "} ",
                                   2)
        request, params = setParam(request, params, synch, "{0}.synch={" + str(len(params)) + "} ", 2)

        return [{
            "student_id": str(res[0]),
            "id": str(res[1])
        }
            for res in self.sql_request(request, *tuple(params))]

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

    def add_visit(self, student_id: int, lesson_id: int):
        r = self.sql_request("INSERT INTO {0}(student_id, id, synch) VALUES ({1}, {2}, {3})",
                             config.visitation,
                             student_id,
                             lesson_id,
                             0)
        print("new visit", student_id, lesson_id, r)
        return r

    def complete_lesson(self, lesson_id: int):
        r = self.sql_request("UPDATE {0} SET completed=1 WHERE id={1}",
                             config.lessons,
                             lesson_id)
        return r

    def update_lesson_date(self, lesson_id: int, new_date: datetime):
        # TODO send update on server
        r = self.sql_request("UPDATE {0} SET date='{1}' WHERE id={2}",
                             config.lessons,
                             new_date.strftime("%d-%m-%Y %I:%M%p"),
                             lesson_id)

    def connect2(self) -> sqlite3.Connection or MySQLdb.Connection:
        try:
            if config.db == "sqlite":
                connection = sqlite3.connect(config.database_path)

                if self.created is None or not self.created:
                    from Main.DataBase.Creator import create
                    create(connection.cursor())
                    self.created = True

            elif config.db == "oracle":
                import cx_Oracle
                connection = cx_Oracle.Connection(config.connection)

            elif config.db == "mysql":
                connection = MySQLdb.connect(host=config.db_host,
                                             user=config.db_user,
                                             passwd=config.db_password,
                                             db=config.db_name,
                                             use_unicode=True,
                                             charset='utf8')

        except IOError:
            # если база данных не найдена - завершаем приложение
            print("no db found")
            exit()

        return connection

    def sql_request(self, msg, *args, ignore_banned_symbols=False) -> list:
        """

        :param ignore_banned_symbols: разрешает использовтаь запрщенные символы
        :param msg: Содержит шаблон строки запроса
        :param args: Аргументы для форматирования запроса
        :return: Возвращает результат SQL запроса
        :rtype: list
        """

        conn = self.connect2()
        cursor = conn.cursor()

        message = msg.replace('\t', '').replace("  ", " ")

        arg = args if ignore_banned_symbols else valid(*args)

        try:
            sql = message.format(*arg)
            Logger.write(sql)
            try:
                cursor.execute(sql)
            # except (AttributeError, MySQLdb.OperationalError, sqlite3.ProgrammingError):
            #     cursor = self.connection.cursor()
            #     cursor.execute(sql)
            except sqlite3.OperationalError as e:
                Logger.write("index out of range {0} in {1}".format(arg, message))
                print("SQL INSERT ERROR: ->", sql, e)
                traceback.print_stack()
                return []
            conn.commit()

            temp = cursor.fetchall()
        except IndexError as e:
            print("SQL FORMAT ERROR: ->", e)
            traceback.print_exc()

        return temp

    def get_table2(self, owner, student_id=None, professor_id=None, group_id=None, discipline_id=None):
        if owner == "student":
            request = "SELECT DISTINCT {0}.date, {2}.name FROM {0} " \
                      "JOIN {1} ON {1}.id={0}.id " \
                      "JOIN {2} ON {0}.discipline_id={2}.id " \
                      "JOIN {3} ON {3}.group_id={0}.group_id " \
                      "WHERE {0}.discipline_id IN {4} AND {3}.student_id={5} " \
                      "ORDER  BY {0}.date"
            params = [config.lessons,
                      config.visitation,
                      config.disciplines,
                      config.students_groups,
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
            params = [config.lessons,
                      config.visitation,
                      config.disciplines,
                      discipline_id if discipline_id is tuple else "({})".format(discipline_id),
                      student_id]
            visit = self.sql_request(request, *tuple(params))
            print(visit)
            for v in visit:
                data[v[1]][v[0]] = True
        return data

    def get_auth(self, professor_id) -> list:
        req = "SELECT card_id, password FROM {0} WHERE user_id={1}"
        params = [config.auth, professor_id]

        res = self.sql_request(req, *tuple(params))

        return [{
            "card_id": i[0],
            "password": i[1]
        } for i in res]

    def start_lesson(self, lesson_id=None):
        req = "UPDATE {} SET completed=1 WHERE id={}"
        params = [config.lessons, lesson_id]

        res = self.sql_request(req, *tuple(params))

        return res

    def add_card_id_to(self, card_id: int, student_id=None):
        req = "UPDATE {} SET card_id={} WHERE id={}"
        params = [config.students,
                  card_id,
                  student_id]

        res = self.sql_request(req, *tuple(params))
        return res


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
    for banned_symbol in config.sql_banned_symbols:
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
