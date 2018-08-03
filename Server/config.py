"""
    config
"""
db = "mysql"
if db == "sqlite":
    database_path = "db.db"
if db == "oracle":
    connection = ""
    db_user = ""
    db_password = ""
if db == "mysql":
    db_user="pythonserver"
    db_password="bisitor123456"
    db_host= "localhost"
    db_name="pythonserver"
    pass

logger = "logger.txt"
visitation = "visitations"
auth = "auth5"
password = "123457"
students = "students"
professors = "professors"
groups = "groups"
students_groups = "students_groups"
disciplines = "disciplines"
lessons = "lessons"
rooms = "rooms"
notification = "notification"
parents = "parent"
parents_students = "parents_students"
loss = "loss"
notification_params = "notification_params"
sql_banned_symbols = ["\'", ";", "\""]
session_life = "57600"
email = "vladschekochikhin@gmail.com"
telegram_url=""

