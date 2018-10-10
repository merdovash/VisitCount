"""
    sql_handler.py
"""
import contextlib
import sqlite3
from typing import Dict, List, Any

import pymysql

from DataBase.Types import AtrDict, Table, Column
from DataBase.config2 import DataBaseConfig, DataBaseType


def log(text: str):
    """

    :param text: string, value to write
    """
    with open("logger.txt", "a+") as logger:
        logger.write(str(text) + "\n")
        logger.close()


class DataBase:
    __slots__ = ('connection', 'config', '_last_error')
    """
    Base class of sqlDataBase wrapper
    """

    class Schema(object):
        auth = Table(
            'auth5',
            AtrDict({
                'id': Column('id', 'INTEGER', primary_key=True),
                'login': Column('login', 'TEXT', unique=True),
                'password': Column('password', 'TEXT'),
                'user_id': Column('user_id', 'INT'),
                'user_type': Column('user_type', 'INT'),
                'uid': Column('uid', 'TEXT', unique=True),
                'card_id': Column('card_id', 'TEXT'),
            }),
            "")
        students = Table(
            'students',
            AtrDict({
                'id': Column('id', 'INTEGER', primary_key=True),
                'last_name': Column('last_name', 'TEXT'),
                'first_name': Column('first_name', 'TEXT'),
                'middle_name': Column('middle_name', 'TEXT'),
                'card_id': Column('card_id', 'TEXT')
            }),
            ""
        )
        professors = Table(
            'professors',
            AtrDict({
                'id': Column('id', 'INTEGER', primary_key=True),
                'last_name': Column('last_name', 'TEXT'),
                'first_name': Column('first_name', 'TEXT'),
                'middle_name': Column('middle_name', 'TEXT'),
                'card_id': Column('card_id', 'TEXT')
            }),
            ""
        )
        parents = Table(
            'parents',
            AtrDict({
                'id': Column('id', 'INTEGER', primary_key=True),
                'last_name': Column('last_name', 'TEXT'),
                'first_name': Column('first_name', 'TEXT'),
                'middle_name': Column('middle_name', 'TEXT'),
                'email': Column('email', 'TEXT')
            }),
            ''
        )
        groups = Table(
            'groups',
            AtrDict({
                'id': Column('id', 'INTEGER', primary_key=True),
                'name': Column('name', 'TEXT')
            }),
            ''
        )
        lessons = Table(
            'lessons',
            AtrDict({
                'id': Column('id', 'INTEGER', primary_key=True),
                'professor_id': Column('professor_id', 'INT'),
                'group_id': Column('group_id', 'INT'),
                'discipline_id': Column('discipline_id', 'INT'),
                'date': Column('date', 'DATE'),
                'room_id': Column('room_id', 'TEXT'),
                'type': Column('type', 'INT'),
                'completed': Column('completed', 'INT')
            }),
            ''
        )
        visitations = Table(
            'visitations',
            AtrDict({
                'id': Column('id', 'INTEGER', primary_key=True),
                'student_id': Column('student_id', 'INT', ''),
                'lesson_id': Column('lesson_id', 'INT', '')
            }),
            '')
        students_groups = Table(
            'students_groups',
            AtrDict({
                'student_id': Column('student_id', 'INT'),
                'group_id': Column('group_id', 'INT')
            }),
            ''
        )
        disciplines = Table(
            'disciplines',
            AtrDict({
                'id': Column('id', 'INTEGER', primary_key=True),
                'name': Column('name', 'TEXT')
            }),
            '')
        updates = Table(
            'updates',
            AtrDict({
                'id': Column('id', 'INTEGER', primary_key=True),
                'table_name': Column('table_name', 'TEXT'),
                'row_id': Column('row_id', 'INT')
            }),
            ''
        )
        professors_updates = Table(
            'professors_updates',
            AtrDict({
                'professor_id': Column('professor_id', 'INT'),
                'update_id': Column('update_id', 'INT')
            }),
            ''
        )

        @classmethod
        def tables(cls) -> List[Table]:
            attributes = [cls.__dict__[i] for i in cls.__dict__ if not i.startswith('__') and i != 'tables']
            # print(attributes)
            return attributes

        @classmethod
        def __getitem__(cls, item):
            return cls.__dict__[item]

    updatable_tables = [Schema.students.name,
                        Schema.lessons.name,
                        Schema.visitations.name,
                        Schema.professors.name]

    def __init__(self, config=None):
        if config is not None:
            self.config: DataBaseConfig = config
        else:
            self.config: DataBaseConfig = DataBaseConfig()

        self.connection = self.connect()

        self._last_error = ""

        if self.config.check_tables:
            self.check_tables()

    def __del__(self):
        self.connection.close()

    def check_tables(self):
        """
        Checks whether all tables exist
        If table is not exist it will create table from schema
        """
        with contextlib.closing(self.connection.cursor()) as cursor:
            for table in DataBase.Schema.tables():
                try:
                    cursor.execute("SELECT count(*) FROM {}".format(table.name))
                except (pymysql.err.ProgrammingError, sqlite3.OperationalError) as e:
                    print(f'table {table}, {e}')
                    self.create_table(table, cursor)
                except pymysql.ProgrammingError:
                    self.create_table(table, cursor)

    def create_table(self, table: Table, cursor):
        """
        Creates table from schema by name

        :param table: name of table that needs to de created
        """

        def primary_key():
            if self.config.db_type == DataBaseType.MYSQL:
                return 'PRIMARY KEY AUTO INCREMENT'
            elif self.config.db_type == DataBaseType.SQLITE:
                return 'PRIMARY KEY AUTOINCREMENT'
            return ''

        req = "CREATE TABLE {0} ({1} {2});".format(
            table.name,
            ', '.join(["{} {} {} {}".format(
                column.name,
                column.type,
                primary_key() if column.primary_key else '',
                'UNIQUE' if column.unique else ''
            )
                for column in table.columns.values()]),
            ', ' + table.extra if table.extra != '' else ''
        )
        # print(req)

        cursor.execute(req)
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
            if self.config.db_type == DataBaseType.MYSQL:
                import pymysql
                self.connection = pymysql.connect(**self.config.db)
            elif self.config.db_type == DataBaseType.SQLITE:
                import sqlite3 as sqlite
                self.connection = sqlite.connect(**self.config.db)

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

        temp = None

        with contextlib.closing(self.connection.cursor()) as cursor:
            try:
                sql = message.format(*arg)

                if self.config.print:
                    # print(sql)
                    pass

                cursor.execute(sql)
                self.connection.commit()

                temp = cursor.fetchall()
            except IndexError:
                self._last_error = 'internal error @ request syntax'
            except Exception as exception:
                self._last_error = f'internal error @ {str(exception)}'

            if self.config.print:
                # print(temp)
                pass


        return temp

    def field_updated(self, table, row_id, professor_id):
        """

        Function logs updates.

        :param table: table updated
        :param row_id: id of row that have been updated
        :param professor_id: ID of professor changed data
        """

        def no_such_update():
            updates_list = self.sql_request(
                f"""
                SELECT id 
                FROM updates 
                WHERE table_name='{table}' AND row_id={row_id};""")

            updates_count = len(updates_list)
            return updates_count == 0

        if no_such_update():
            with contextlib.closing(self.connection.cursor()) as cursor:
                req = """
                INSERT INTO {0} (table_name, row_id) 
                VALUES ('{1}',{2});
                """.format(DataBase.Schema.updates.name, table, row_id)

                cursor.execute(req)

                update_id = cursor.lastrowid
        else:
            update_id = self.sql_request(f"""
                SELECT id 
                FROM updates 
                WHERE table_name='{table}' AND row_id={row_id};""")[0][0]

        # print(update_id)

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

        if professor_id is not None and professor_id in professors_list:
            # print(professors_list, professor_id, professor_id in professors_list)
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
                             DataBase.Schema.updates.name,
                             DataBase.Schema.professors_updates.name,
                             professor_id)
        return r

    def to_dict(self, list_of_tuple, table) -> List[Dict[str, str or int]]:
        if self.config.db_type == DataBaseType.SQLITE:
            rule = self.sql_request("PRAGMA table_info({})", table)
            col = 1
        elif self.config.db_type == DataBaseType.MYSQL:
            rule = self.sql_request("SHOW COLUMNS FROM {}", table)
            col = 0
        else:
            raise Exception('no such database')

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

        def ids_to_remove():
            return ', '.join(str(i[0]) for i in self.sql_request("""
                SELECT {0}.{1}
                FROM {0}
                LEFT JOIN {2} ON {0}.{1}={2}.{3}
                WHERE {2}.{4} IS NULL""",
                                                                 DataBase.Schema.updates.name,
                                                                 DataBase.Schema.updates.columns.id.name,
                                                                 DataBase.Schema.professors_updates.name,
                                                                 DataBase.Schema.professors_updates.columns.update_id.name,
                                                                 DataBase.Schema.professors_updates.columns.professor_id.name))

        # find all updates
        with contextlib.closing(self.connection.cursor()) as cursor:
            count = cursor.execute('SELECT Count(*) FROM {0} WHERE {1}={2}'.format(
                DataBase.Schema.professors_updates.name,
                DataBase.Schema.professors_updates.columns.professor_id.name,
                professor_id
            ))

            # remove from professor_updates
            cursor.execute('DELETE FROM {0} WHERE {1}={2}'.format(
                DataBase.Schema.professors_updates.name,
                DataBase.Schema.professors_updates.columns.professor_id.name,
                professor_id
            ))

            # remove from updates
            ids = ids_to_remove()
            if len(ids) > 0:
                req = """
                DELETE FROM {0} 
                WHERE {0}.{1} IN ({2})""".format(
                    DataBase.Schema.updates.name,
                    DataBase.Schema.updates.columns.id.name,
                    ids
                )
                cursor.execute(req)

        return count

    def set_updates(self, data: Dict[str, List[Dict[str, str or int]]], professor_id=None, fix=True):
        """

        :param data:
        :param professor_id:
        :param fix:
        """
        for table in data.keys():
            if table in DataBase.updatable_tables:
                for case in data[table]:

                    if table == DataBase.Schema.visitations.name:
                        row_id = self.add_visitation(**case)
                    else:
                        row_id = case['id']
                        case.pop('id', None)
                        print('case', case)
                        self.update(table, row_id, case)

                    # if it primary update
                    if fix:
                        self.field_updated(table=table,
                                           row_id=row_id,
                                           professor_id=professor_id)

    def add_visitation(self, student_id, lesson_id, id=None):
        """
        Insert new visitation

        :param student_id: ID of student
        :param lesson_id: ID of lesson
        :return: ID of row
        """
        self.sql_request("""
        INSERT INTO {0}({3}, {4}) 
        VALUES({1}, {2});""",
                         DataBase.Schema.visitations.name,
                         student_id,
                         lesson_id,
                         DataBase.Schema.visitations.columns.student_id.name,
                         DataBase.Schema.visitations.columns.lesson_id.name)
        res = self.sql_request("""
        SELECT id 
        FROM {0} 
        WHERE student_id={1} AND lesson_id={2}""",
                               DataBase.Schema.visitations.name,
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
            ', '.join("{name}='{value}'".format(**{'name': key, 'value': data[key]}) for key in data),
            row_id
        )
        # print(table, req)
        self.sql_request(req)


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
