class DataBaseConfig:
    def __init__(self):
        self.db = 'sqlite'
        if self.db == "mysql":
            self.db_user = "pythonserver"
            self.db_password = ""
            self.db_host = "localhost"
            self.db_name = "pythonserver"
        elif self.db == "sqlite":
            self.database_path = "C:\\Users\\MERDovashkinar\\PycharmProjects\\VisitCount\\db.db"
        elif self.db == 'oracle':
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
        self.parents = "parents"
        self.parents_students = "parents_students"
        self.loss = "loss"
        self.notification_params = "notification_params"
        self.sql_banned_symbols = ["\'", ";", "\""]
        self.session_life = "57600"
        self.email = "valeraolegovna228@gmail.com"
        self.main_button_css = "background-color: #ff8000; color: #ffffff; font-weight: bold;"
