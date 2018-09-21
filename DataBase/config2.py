import os


class DataBaseType(int):
    SQLITE = 0
    MYSQL = 1


class DataBaseConfig:
    def __init__(self):
        self.server = "http://bisitor.itut.ru"
        self.db_type = DataBaseType.SQLITE
        self.check_tables = True
        self.print = False
        if self.db_type == DataBaseType.MYSQL:
            self.db = {
                "host": "localhost",
                "user": "pythonserver",
                "password": "bisitor123456",
                "database": "pythonserver",
                "use_unicode": True,
                "charset": 'utf8'
                # 'cursorclass': pymysql.cursors.DictCursor
            }
        elif self.db_type == DataBaseType.SQLITE:
            self.db = {
                "database": os.path.abspath("DataBase2\\db.db"),
                "check_same_thread": False
            }
            print('database path:', self.db['database'])
        elif self.db_type == 'oracle':
            self.connection = ""
        self.logger = "logger.txt"
        self.sql_banned_symbols = ["\'", ";", "\""]
        self.session_life = "57600"
        self.email = "valeraolegovna228@gmail.com"
        self.main_button_css = "background-color: #ff8000; color: #ffffff; font-weight: bold;"
