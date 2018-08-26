

class DataBaseConfig:
    def __init__(self):
        self.server = "http://bisitor.itut.ru"
        self.db_type = 'sqlite'
        self.check_tables = True
        self.print = False
        if self.db_type == "mysql":
            import pymysql
            self.db = {
                "host": "localhost",
                "user": "pythonserver",
                "password": "bisitor123456",
                "db": "pythonserver",
                "use_unicode": True,
                "charset": 'utf8',
                # 'cursorclass': pymysql.cursors.DictCursor
            }
        elif self.db_type == "sqlite":
            self.db = {
                "database": "C:\\Users\\MERDovashkinar\\PycharmProjects\\VisitCount\\db.db",
                "check_same_thread": False
            }
        elif self.db_type == 'oracle':
            self.connection = ""
        self.logger = "logger.txt"
        self.visitation = "visitations"
        self.auth = "auth5"
        self.password = "123457"
        self.students = "students"
        self.professors = "professors"
        self.groups = "groups"
        self.students_groups = "students_groups"
        self.disciplines = "disciplines"
        self.lessons = "lessons"
        self.rooms = "rooms"
        self.notification = "notification"
        self.updates = "updates"
        self.professors_updates = "professors_updates"
        self.parents = "parents"
        self.parents_students = "parents_students"
        self.loss = "loss"
        self.notification_params = "notification_params"
        self.sql_banned_symbols = ["\'", ";", "\""]
        self.session_life = "57600"
        self.email = "valeraolegovna228@gmail.com"
        self.main_button_css = "background-color: #ff8000; color: #ffffff; font-weight: bold;"
