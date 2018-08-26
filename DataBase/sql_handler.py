"""
    sql_handler.py
"""
from datetime import datetime
from typing import Dict, List, Any, Iterable

import pymysql

from DataBase.Types import AtrDict, Table, Column
from DataBase.config2 import DataBaseConfig


def log(text: str):
    """

    :param text: string, value to write
    """
    with open("logger.txt", "a+") as logger:
        logger.write(str(text) + "\n")
        logger.close()


class DataBase:
    """
    Base class of sqlDataBase wrapper
    """

    class Schema(object):
        auth = Table(
            'auth5',
            AtrDict({
                'id': Column('id', 'INTEGER', 'PRIMARY KEY AUTOINCREMENT '),
                'login': Column('login', 'TEXT', 'UNIQUE'),
                'password': Column('password', 'TEXT', ''),
                'user_id': Column('user_id', 'INT', ''),
                'user_type': Column('user_type', 'INT', ''),
                'uid': Column('uid', 'TEXT', 'UNIQUE'),
                'card_id': Column('card_id', 'TEXT', ''),
            }),
            "")
        students = Table(
            'students',
            AtrDict({
                'id': {
                    'name': 'id',
                    'type': 'INTEGER',
                    'spec': 'PRIMARY KEY AUTOINCREMENT '
                },
                'last_name': {
                    'name': 'last_name',
                    'type': 'TEXT',
                    'spec': ''
                },
                'first_name': {
                    'name': 'first_name',
                    'type': 'TEXT',
                    'spec': ''
                },
                'middle_name': {
                    'name': 'middle_name',
                    'type': 'TEXT',
                    'spec': ''
                },
                'card_id': {
                    'name': 'card_id',
                    'type': 'TEXT',
                    'spec': ''
                }
            }),
            ""
        )
        professors = Table(
            'professors',
            AtrDict({
                'id': {
                    'name': 'id',
                    'type': 'INTEGER',
                    'spec': 'PRIMARY KEY AUTOINCREMENT '
                },
                'last_name': {
                    'name': 'last_name',
                    'type': 'TEXT',
                    'spec': ''
                },
                'first_name': {
                    'name': 'first_name',
                    'type': 'TEXT',
                    'spec': ''
                },
                'middle_name': {
                    'name': 'middle_name',
                    'type': 'TEXT',
                    'spec': ''
                },
                'card_id': {
                    'name': 'card_id',
                    'type': 'TEXT',
                    'spec': ''
                }
            }),
            ""
        )
        parents = Table(
            'parents',
            AtrDict({
                'id': {
                    'name': 'id',
                    'type': 'INTEGER',
                    'spec': 'AUTOINCREMENT'
                },
                'last_name': {
                    'name': 'last_name',
                    'type': 'TEXT',
                    'spec': ''
                },
                'first_name': {
                    'name': 'first_name',
                    'type': 'TEXT',
                    'spec': ''
                },
                'middle_name': {
                    'name': 'middle_name',
                    'type': 'TEXT',
                    'spec': ''
                },
                'email': {
                    'name': 'email',
                    'type': 'TEXT',
                    'spec': ''
                }
            }),
            ''
        )
        groups = Table(
            'groups',
            AtrDict({
                'id': {
                    'name': 'id',
                    'type': 'INTEGER',
                    'spec': 'PRIMARY KEY AUTOINCREMENT'
                },
                'name': {
                    'name': 'name',
                    'type': 'TEXT',
                    'spec': ''
                }
            }),
            ''
        )
        lessons = Table(
            'lessons',
            AtrDict({
                'id': {
                    'name': 'id',
                    'type': 'INTEGER',
                    'spec': 'PRIMARY KEY AUTOINCREMENT'
                },
                'professor_id': {
                    'name': 'professor_id',
                    'type': 'INT',
                    'spec': ''
                },
                'group_id': {
                    'name': 'group_id',
                    'type': 'INT',
                    'spec': ''
                },
                'discipline_id': {
                    'name': 'discipline_id',
                    'type': 'INT',
                    'spec': ''
                },
                'date': {
                    'name': 'date',
                    'type': 'DATE',
                    'spec': ''
                },
                'room_id': {
                    'name': 'room_id',
                    'type': 'TEXT',
                    'spec': ''
                },
                'type': {
                    'name': 'type',
                    'type': 'INT',
                    'spec': ''
                },
                'completed': {
                    'name': 'completed',
                    'type': 'INT',
                    'spec': ''
                }
            }),
            ''
        )
        visitations = Table(
            'visitations',
            AtrDict({
                'id': Column('id', 'INT', 'PRIMARY KEY AUTOINCREMENT'),
                'student_id': Column('student_id', 'INT', ''),
                'lesson_id': Column('lesson_id', 'INT', '')
            }),
            '')
        students_groups = Table(
            'students_groups',
            AtrDict({
                'student_id': {
                    'name': 'student_id',
                    'type': 'INT',
                    'spec': ''
                },
                'group_id': {
                    'name': 'group_id',
                    'type': 'INT',
                    'spec': ''
                }
            }),
            ''
        )
        disciplines = Table(
            'disciplines',
            AtrDict({
                'id': {
                    'name': 'id',
                    'type': 'INTEGER',
                    'spec': 'PRIMARY KEY AUTOINCREMENT'
                },
                'name': {
                    'name': 'name',
                    'type': 'TEXT',
                    'spec': ''
                }
            }),
            '')
        updates = Table(
            'updates',
            AtrDict({
                'id': {
                    'name': 'id',
                    'type': 'INTEGER',
                    'spec': 'PRIMARY KEY AUTOINCREMENT'
                },
                'table_name': {
                    'name': 'table_name',
                    'type': 'TEXT',
                    'spec': ''
                },
                'row_id': {
                    'name': 'row_id',
                    'type': 'INT',
                    'spec': ''
                }
            }),
            ''
        )
        professors_updates = Table(
            'professors_updates',
            AtrDict({
                'professor_id': {
                    'name': 'professor_id',
                    'type': 'INTEGER',
                    'spec': ''
                },
                'update_id': {
                    'name': 'update_id',
                    'type': 'INT',
                    'spec': ''
                }
            }),
            ''
        )

        @classmethod
        def tables(cls) -> List[Table]:
            attributes = [cls.__dict__[i] for i in cls.__dict__ if not i.startswith('__') and i!='tables']
            print(attributes)
            return attributes

        @classmethod
        def __getitem__(cls, item):
            return cls.__dict__[item]

    updatable_tables = [Schema.students.name, Schema.lessons.name, Schema.visitations.name]

    def __init__(self, config=None):
        if config is not None:
            self.config: DataBaseConfig = config
        else:
            self.config: DataBaseConfig = DataBaseConfig()

        self.connection = self.connect()
        self.cursor = self.connection.cursor()

        self._last_error = ""

        if self.config.check_tables:
            self.check_tables()

    def check_tables(self):
        """
        Checks whether all tables exist
        If table is not exist it will create table from schema
        """
        for table in DataBase.Schema.tables():
            try:
                self.cursor.execute("SELECT count(*) FROM {}".format(table.name))
            except pymysql.ProgrammingError as e:
                print(f'table {table}, {e}')
                self.create_table(table)

    def create_table(self, table: Table):
        """
        Creates table from schema by name

        :param table: name of table that needs to de created
        """
        req = "CREATE TABLE {0} ({1} {2});".format(
            table.name,
            ', '.join([f"{rule.name} {rule.type} {rule.spec}"
                       for rule in table.columns.values()]),
            ', ' + table.extra
        )
        print(req)
        self.cursor.execute(req)

        self.connection.commit()

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
            if self.config.db_type == "mysql":
                import pymysql
                self.connection = pymysql.connect(**self.config.db)
            elif self.config.db_type == "sqlite":
                import sqlite3 as sqlite
                self.connection = sqlite.connect(**self.config.db)

        _connect()
        self.cursor = self.connection.cursor()
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

        cursor = self.cursor
        try:
            sql = message.format(*arg)
            if self.config.print:
                print(sql)
            cursor.execute(sql)
            self.connection.commit()
        except IndexError:
            self._last_error = 'internal error @ request syntax'
        except Exception as exception:
            self._last_error = f'internal error @ {exception}'

        temp = cursor.fetchall()
        if self.config.print:
            print(temp)
        return temp

    def field_updated(self, table, row_id, professor_id):
        """

        Function logs updates.

        :param table: table updated
        :param row_id: id of row that have been updated
        :param professor_id: ID of professor changed data
        """
        updates_list = self.sql_request("""
        SELECT id 
        FROM updates 
        WHERE table_name='{0}' AND row_id={1};""",
                                        table,
                                        row_id)
        updates_count = len(updates_list)
        if updates_count == 0:
            req = """
            INSERT INTO {0} (table_name, row_id) 
            VALUES ('{1}',{2});""".format(self.config.updates, table, row_id)
            self.sql_request(req)
            update_id = self.cursor.lastrowid
        else:
            update_id = updates_list[0][0]

        print(update_id)

        professors_list = self._get_professors_for_update(table, row_id, professor_id=professor_id)

        self._insert_professors_updates(update_id, professors_list)

    def _get_professors_for_update(self, table, row_id, professor_id=None):
        professors_list = []

        if table == DataBase.Schema.students.name:
            professors_list = [i[0]
                               for i in self.sql_request("""
                    SELECT DISTINCT professor_id 
                    FROM {0} 
                    JOIN {1} ON {0}.group_id={1}.group_id 
                    WHERE {1}.student_id={2}""",
                                                         DataBase.Schema.lessons.name,
                                                         DataBase.Schema.students_groups.name,
                                                         row_id)]

        elif table == DataBase.Schema.visitations.name:
            professors_list = [i[0] for i in self.sql_request("""
                    SELECT professor_id 
                    FROM {0} 
                    JOIN {1} ON {0}.id={1}.lesson_id 
                    WHERE {1}.lesson_id={2}""",
                                                              DataBase.Schema.lessons.name,
                                                              DataBase.Schema.visitations.name,
                                                              row_id)]

        if professor_id is not None:
            print(professors_list, professor_id, professor_id in professors_list)
            professors_list.remove(professor_id)

        return professors_list

    def _insert_professors_updates(self, update_id, professors):
        def __values__():
            return ','.join(
                ["({}, {})".format(update_id, professor_id) for professor_id in professors])

        if professors:
            req = """
            insert into {0}(update_id, professor_id) 
            Values {1}""".format(DataBase.Schema.professors_updates.name, __values__())

            self.sql_request(req)

    def get_updates_list(self, professor_id):
        """

        :param professor_id: ID of professor that needs to synchronize changes
        :return: list of update's ID
        """
        r = self.sql_request("""
        SELECT DISTINCT table_name, row_id 
        FROM {0} 
        JOIN {1} ON {0}.id={1}.update_id 
        WHERE {1}.professor_id = {2}""",
                             self.config.updates,
                             self.config.professors_updates,
                             professor_id)
        return r

    def to_dict(self, list_of_tuple, table) -> List[Dict[str, str or int]]:
        if self.config.db_type == "sqlite":
            rule = self.sql_request("PRAGMA table_info({})", table)
            col = 1
        elif self.config.db_type == "mysql":
            rule = self.sql_request("SHOW COLUMNS FROM {}", table)
            col = 0
        else:
            raise Exception('no such db')

        list_of_dict = []
        for case in list_of_tuple:
            list_of_dict.append({rule[i][col]: case[i] for i in range(len(rule))})

        return list_of_dict

    def get_updates(self, professor_id) -> Dict[str, List[Dict[str, Any]]]:
        """

        :param professor_id: ID of professors that request updates
        :return: dictionary of (table, list of new data)
        """

        def sort_by_table(updates_list) -> Dict[str, List[Dict[str, Any]]]:
            sorted_updates = {}
            for update in updates_list:
                if update[0] not in sorted_updates:
                    sorted_updates[update[0]] = []
                sorted_updates[update[0]].append(update[1])
            return sorted_updates

        updates_list = sort_by_table(self.get_updates_list(professor_id))

        updates = {}
        for table in updates_list:
            updates[table] = self.to_dict(
                self.sql_request("SELECT * FROM {0} WHERE id IN ({1})",
                                 table,
                                 ', '.join([str(i) for i in updates_list[table]])),
                table)
        return updates

    def remove_updates(self, professor_id: int) -> int:
        """
        removes updates that are no longer needed

        :param professor_id: ID of professor that gets updates
        """

        def _list_of_id_(updates_id: Iterable) -> str:
            return ', '.join([i[0] for i in updates_id])

        # find all updates
        ids = self.sql_request("""
        SELECT id 
        FROM {0} 
        JOIN {1} ON {0}.id={1}.update_id 
        WHERE {1}.professor_id={2}""",
                               self.config.updates,
                               self.config.professors_updates,
                               professor_id)

        count_updates = len(ids)

        # delete updates
        self.sql_request("""
        DELETE FROM {0} 
        WHERE {1} IN ({2})""".format(
            DataBase.Schema.updates.name,
            DataBase.Schema.updates.columns.id,
            _list_of_id_(set(ids))))

        # delete professors_updates
        self.sql_request("""
        DELETE FROM {0} 
        WHERE {1}={2}""",
                         DataBase.Schema.professors_updates.name,
                         DataBase.Schema.professors_updates.columns.professor_id.name,
                         professor_id)

        return count_updates

    def set_updates(self, data: Dict[str, List[Dict[str, str or int]]], professor_id=None, fix=True):
        """

        :param data:
        :param professor_id:
        :param fix:
        """
        for table in data.keys():
            if table in DataBase.updatable_tables:
                for case in data[table]:

                    if table == self.config.visitation:
                        row_id = self.add_visitation(**case)
                    else:
                        row_id = case['id']
                        self.update(table, row_id, case)

                    # if it primary update
                    if fix:
                        self.field_updated(table=table,
                                           row_id=row_id,
                                           professor_id=professor_id)

    def add_visitation(self, student_id, lesson_id, id):
        """
        Insert new visitation

        :param student_id: ID of student
        :param lesson_id: ID of lesson
        :return: ID of row
        """
        self.sql_request("""
        INSERT INTO {0}(student_id, lesson_id) 
        VALUES({1}, {2});""",
                         self.config.visitation,
                         student_id,
                         lesson_id)
        res = self.sql_request("""
        SELECT id 
        FROM {0} 
        WHERE student_id={1} AND lesson_id={2}""",
                               self.config.visitation,
                               student_id,
                               lesson_id)

        return res[0][0]

    def loads(self, table, data: List[Dict[str, Any]]):
        """
        Inserts data into table
        :param table: table name (Not None)
        :param data: list of data to insert
        """

        if data:
            keys = data[0].keys()
            req = "INSERT INTO {0}({1}) VALUES {2};".format(
                table,
                ', '.join(keys),
                ','.join(['(' + ','.join([f"'{str(d[key])}'" for key in keys]) + ')' for d in data]))
            self.sql_request(req)

    def update(self, table, row_id, data):
        """
        update data in table

        :param table: table name
        :param row_id: ID of row
        :param data: new data
        """
        req = "UPDATE {0} SET {1} WHERE id={2}".format(
            table,
            ', '.join(["{name}='{value}'".format(**{'name': key, 'value': data[key]}) for key in data]),
            row_id
        )
        print(req)
        self.sql_request(req)


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

        results_count = len(res)
        return results_count > 0

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

            if res:
                return {
                    "type": res[0][0],
                    "user_id": res[0][1],
                    "id": res[0][2]
                }
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

    def get_auth_info(self, professor_id: int or str) -> List[Dict[str, Any]]:
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
        self.sql_request("""
            UPDATE {0}
            SET uid='{1}'
            WHERE id={2}
        """,
                         self.config.auth,
                         uid,
                         account_id)

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

    def set_request_params(self, request: str, params: list, param, string: str, size: int):
        """

        :param request: request string
        :param params: list of format params of request
        :param param: new parameter
        :param string: name of parameter
        :param size: maximum count of params that allows not to set 'AND' keyword
        :return: new request and new params
        """
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
            request, params = self.set_request_params(request, params, group_id,
                                                      "{1}.group_id={" + str(len(params)) + "} ", 2)
            request, params = self.set_request_params(request, params, discipline_id,
                                                      "{1}.discipline_id={" + str(len(params)) + "} ", 2)
        request, params = self.set_request_params(request, params, professor_id, "{0}.id={" + str(len(params)) + "} ",
                                                  1)
        request, params = self.set_request_params(request, params, card_id, "{0}.card_id={" + str(len(params)) + "} ",
                                                  1)

        return [
            {
                "first_name": res[0],
                "last_name": res[1],
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

    def get_group_visit(self, professor_id=None, *args):
        dates = [{'id': i, 'name': i} for i in range(18)]
        rows = [{'id': i[0], 'name': i[1]} for i in self.sql_request("""
        SELECT {0}.id, {0}.name 
        FROM {0} 
        JOIN {1} ON {0}.id={1}.group_id
        WHERE {1}.professor_id={2}""",
                                                                     self.config.groups,
                                                                     self.config.lessons,
                                                                     professor_id)]
        visit = [[i[2], i[1], i[0]] for i in self.sql_request("""
        SELECT count({1}.lesson_id)/count({0}.id), {1}.group_id, WEEK({0}.date) as 'week' 
        FROM {0}
        JOIN {1} ON {1}.lesson_id={0}.id
        LEFT JOIN {2} ON {2}.student_id={1}.student_id AND {1}.lesson_id={0].id
        WHERE {0}.professor_id={3}
        GROUP BY {0}.group_id, week""",
                                                              self.config.visitation,
                                                              self.config.lessons,
                                                              self.config.students_groups,
                                                              professor_id)]

        return {
            'dates': dates,
            'rows': rows,
            'visit': visit
        }

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
            request, params = self.set_request_params(request, params, professor_id,
                                                      "{1}.professor_id={" + str(len(params)) + "} ", 2)
            request, params = self.set_request_params(request, params, discipline_id,
                                                      "{1}.discipline_id={" + str(len(params)) + "} ", 2)
        request, params = self.set_request_params(request, params, group_id, "{0}.id={" + str(len(params)) + "}", 2)

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
        request, params = self.set_request_params(request, params, professor_id,
                                                  "{1}.professor_id={" + str(len(params)) + "} ",
                                                  2)
        request, params = self.set_request_params(request, params, discipline_id, "{0}.id={" + str(len(params)) + "} ",
                                                  2)
        request, params = self.set_request_params(request, params, group_id, "{1}.group_id={" + str(len(params)) + "} ",
                                                  2)

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
            request, params = self.set_request_params(request, params, professor_id,
                                                      "{2}.professor_id={" + str(len(params)) + "} ", 3)
            request, params = self.set_request_params(request, params, group_id,
                                                      "{1}.group_id={" + str(len(params)) + "} ", 3)
        request, params = self.set_request_params(request, params, student_list,
                                                  "{0}.id IN {" + str(len(params)) + "} ", 1)
        request, params = self.set_request_params(request, params, student_id, "{0}.id={" + str(len(params)) + "} ", 1)
        request, params = self.set_request_params(request, params, card_id, "{0}.card_id={" + str(len(params)) + "} ",
                                                  1)

        return [
            {
                "id": str(res[0]),
                "last_name": res[2],
                "first_name": res[1],
                "middle_name": res[3],
                "card_id": str(res[4])
            }
            for res in self.sql_request(request, *tuple(params))]

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
        request, params = self.set_request_params(request, params, group_id, "{0}.group_id={" + str(len(params)) + "} ",
                                                  1)
        request, params = self.set_request_params(request, params, professor_id,
                                                  "{0}.professor_id={" + str(len(params)) + "} ",
                                                  1)
        request, params = self.set_request_params(request, params, discipline_id,
                                                  "{0}.discipline_id={" + str(len(params)) + "} ",
                                                  1)
        request, params = self.set_request_params(request, params, lesson_id, "{0}.id={" + str(len(params)) + "} ", 1)

        request += "ORDER BY {0}.date "

        return [
            {
                'id': str(res[0]),
                'date': str(res[1]),
                'room_id': str(res[2]),
                'group_id': str(res[3]),
                'discipline_id': str(res[4]),
                'professor_id': str(res[5]),
                'type': str(res[7]),
                'completed': res[6]
            } for res in self.sql_request(request, *tuple(params))]

    def get_visitations(self, group_id=None, professor_id=None, discipline_id=None,
                        student_list=None, student_id=None, synch=None) -> list:
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
        request, params = self.set_request_params(request, params, group_id, "{1}.group_id={" + str(len(params)) + "} ",
                                                  2)
        request, params = self.set_request_params(request, params, professor_id,
                                                  "{1}.professor_id={" + str(len(params)) + "} ",
                                                  2)
        request, params = self.set_request_params(request, params, discipline_id,
                                                  "{1}.discipline_id={" + str(len(params)) + "} ",
                                                  2)
        request, params = self.set_request_params(request, params, synch, "{0}.synch={" + str(len(params)) + "}", 2)

        return [
            {
                "student_id": str(res[0]),
                "lesson_id": str(res[1])
            } for res in self.sql_request(request, *tuple(params))]

    def get_table(self, student_id=None, professor_id=None,
                  discipline_id=None, group_id=None, user_type=None) -> List or Dict:
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
        new_visit = {
            DataBase.Schema.visitations.name: [
                {
                    DataBase.Schema.visitations.columns.student_id.name: student_id,
                    DataBase.Schema.visitations.columns.lesson_id.name: lesson_id
                }
            ]
        }
        self.set_updates(data=new_visit)

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

    def add_card_id_to(self, card_id: int, student_id: int) -> None:
        update_card_id = {
            DataBase.Schema.students.name: [
                {
                    DataBase.Schema.students.columns.card_id.name: card_id,
                    'id': student_id
                }
            ]
        }
        self.set_updates(update_card_id)

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
