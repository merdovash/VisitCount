"""
    php_server.py
"""

"""
    Server
"""
import _md5
import json
import os
import random
import sqlite3

from flask import Flask, make_response, request

from notification import run as notification
from sql_handler import init_sql_handler, \
    get_groups, get_students, is_login_exist, create_account, auth, \
    get_data_for_student_table, free_uid, set_session, \
    get_professor_info, get_data_for_client, synchronize, get_disciplines

app = Flask(__name__)


def related(a):
    """

    :param a: related path to file
    :return: full file path
    """
    return os.path.join(path, a)


def page(body, *args, part=False, js=False):
    """

    :param body: html body
    :param args: inner html content
    :param part:
    :param js: is javascript file
    :return: complete html page
    """
    if not js:
        if part:
            current_page = open(related(body), encoding='utf-8').read().format(*args)
        else:
            main_body = open(related("Site/head.html"), encoding='utf-8').read()
            # print(main_body)
            current_page = main_body.format(open(related(body), encoding='utf-8').read().format(*args))
    else:
        current_page = open(related(body), encoding='utf-8').read()
    return current_page


def json_read(val):
    """

    :param val: json encoded string
    :return: json object
    """

    def decode(v) -> str:
        # TODO: сделать
        """

        :param v: encoded string
        :return: decoded string
        """
        return v

    return json.loads(decode(val))


def json_create(val):
    """

    :param val: object
    :return: encoded json string
    """

    def encode(v) -> str:
        # TODO: сделать кодировку
        """

        :param v: string
        :return: encoded string
        """
        return v

    return json.dumps(encode(val)).encode("utf-8")


@app.route("/", methods=['GET', 'POST'])
def index():
    """

    :return: index.html
    """
    if request.method == "GET":
        return page("Site/index.html")
    if request.method == "POST":
        print("вот что я получил: ", request.data.decode('utf8').replace("'", '"'), "- конец сообщения")
        data = json_read(request.data.decode('utf8').replace("'", '"'))
        print(data)
        if data["type"] == "first":
            if auth(card_id=data["card_id"], password=data["password"]):
                return json_create(get_data_for_client(data["card_id"]))
            else:
                return json_create("{type: 'first',"
                                   "status: 'ERROR',"
                                   "message: 'auth failed'}")
        elif data["type"] == "sync":
            if auth(data["card_id"], data["password"]):
                status = synchronize(data["data"])
                if status == "OK":
                    return json_create({"type": "sync",
                                        "status": "OK"})
                else:
                    return json_create({"type": "sync",
                                        "status": "ERROR",
                                        "message": status[1]})
            else:
                return json_create({"type": "sync",
                                    "status": "ERROR",
                                    "message": "auth failed"})


@app.route("/register", methods=['GET', 'POST'])
def register():
    """

    :return: register.html if user goes to register page, if he submits register information create new user and
    returns index.html
    """
    if request.method == "GET":
        return page("Site/register.html")
    elif request.method == "POST":
        login = request.form.get("login")
        password = request.form.get("password")
        account_type = request.form.get("type")
        user_id = request.form.get("id")
        create_account(login, password, user_id=user_id, account_type=account_type)
        return page("Site/index.html")


def new_uid():
    """

    :return: new unique session id
    """
    number = (random.random() * 100000000000000000) % 13082761331670031
    value = _md5.md5(str(number).encode()).hexdigest()
    while not free_uid(value):
        number = (random.random() * 100000000000000000) % 13082761331670031
        value = _md5.md5(str(number).encode()).hexdigest()
    return value


@app.route("/login", methods=["POST"])
def log_in():
    """

    :return: check whether user exist. if exist returns cabinet.html and set sessions cookies, if not - sends error msg
    """
    if request.method == "POST":
        login = request.form.get("login")
        password = request.form.get("password")
        user_data = auth(login=login, password=password)
        if user_data:
            print(user_data["id"], config.session_life)
            uid = new_uid()
            set_session(uid=uid, account_id=user_data["id"])
            return json_create({'type': 'login', 'status': 'OK', 'message': uid})
        else:
            return json_create({'type': 'login', 'status': 'ERROR', 'message': 'No such user'})


@app.route("/check_login:<string:login>", methods=["GET"])
def check_login(login):
    """

    :param login: login to check
    :return: is login exist
    """
    if request.method == "GET":
        message = {"answer": None}
        if is_login_exist(login):
            message["answer"] = "YES"
        else:
            message["answer"] = "NO"
        print(json_create(message))
        return json_create(message)


@app.route("/notification")
def note():
    """

    This function execute only for tests
    Real usage should be automatic

    :return: data of loss
    """
    notification(config)
    return str("")


def get_user_information(uid: str) -> (str or int, str or int):
    """

    :param uid: unique session id
    :return: type and id of user
    """
    data = auth(uid=uid)
    return data["type"], data["user_id"]


@app.route("/user_info:<string:uid>", methods=["POST", "GET"])
def get_account_info(uid: str):
    """

    :param uid: уникальный идентификатор сессии
    :return: json string полная информация об аккаунте
    """
    if request.method == "GET":
        data = auth(uid=uid)
        if data["type"] == 0 or data["type"] == "0":
            student_info = get_students(student_id=data["user_id"])[0]
            student_info["user_type"] = "0"
            return json_create(student_info)
        if data["type"] == 1 or data["type"] == "1":
            professor_info = get_professor_info(data["user_id"])[0]
            professor_info["user_type"] = "1"
            return json_create(professor_info)


@app.route("/get_students_list_of_group:<int:group_id>", methods=["POST", "GET"])
def get_students_list_of_group(group_id):
    """

    Возвращает список студентов выбранной группы.

    Формирует ответ в формате:
    {
        "id": id<int>,
        "name":
        {
            0: last_name<str>,
            1: first_name<str>,
            2: middle_name<str>
        }
    }

    :param group_id: идентификатор группы
    :return: json string
    """
    if request.method == "GET":
        val = get_students(group_id)
        return json_create(val)


@app.route("/get_disciplines_list:<string:uid>", methods=["GET", "POST"])
def get_discipline_list(uid):
    """

    Возвращает список дисциплин, связанных с пользователем

    Формирует ответ в формате:
    [{"name": name<str>, "id": id<int>}, ...]

    :return: json string
    """
    if request.method == "GET":

        user_type, user_id = get_user_information(uid=uid)

        data = {"error": "no such user"}

        if user_type == "0" or user_type == 0:
            student_id = user_id

            data = {"data": get_disciplines(student_id=student_id)}

        elif user_type == "1" or user_type == 1:
            professor_id = user_id

            data = {"data": get_disciplines(professor_id=professor_id)}

        return json_create(data)


@app.route("/get_groups_list:<string:uid>:<int:discipline_id>", methods=["GET", "POST"])
def get_group_list(uid, discipline_id):
    """

    Возвращает список групп, которые посещают выбранную дисциплину у выбранного преподавателя

    Формирует ответ в формате:
    {"name": name<str>, "id": id<int>}

    :return: json string
    """
    if request.method == "GET":

        user_type, user_id = get_user_information(uid=uid)

        response = None
        print("user type = ", user_type)
        if user_type == 0 or user_type == "0":

            data = {"onchange": "show_disciplines()",
                    "data": get_groups(user_id)}

            response = make_response(json_create(data))

        elif user_type == 1 or user_type == "1":
            discipline_id = discipline_id

            data = {"onchange": "show_disciplines()",
                    "data": get_groups(user_id, discipline_id)}

            response = make_response(json_create(data))

        return response


@app.route("/get_table:<string:uid>:<int:discipline_id>")
def get_table(uid, discipline_id):
    """

    returns all data for table

    :param uid:
    :param discipline_id:
    :return:
    """
    if request.method == "GET":
        user_type, user_id = get_user_information(uid=uid)

        response = None

        if user_type == 0 or user_type == "0":
            student_id = user_id
            group = get_groups(student_id=student_id)[0]
            data = get_data_for_student_table(student_id=student_id, group_id=group["id"], discipline_id=discipline_id)

            response = make_response(json_create(data))

        return response


@app.route("/css/<string:s>")
def get_css(s: str) -> str:
    """

    :param s: название css файла
    :type s: str
    :return: css файл
    """
    return page("css/" + s, js=True)


@app.route("/javascript/<string:s>")
def get_file(s: str) -> str:
    """

    :param s: file name
    :type s: str
    :return: js file
    """
    return page("javascript/" + s, js=True)


def read_configuration_file(config_path: str):
    """

    :param config_path: path to config.py
    :return: object, containing config attributes
    """

    def create(dictionary):
        """

        :param dictionary: dictionary of attributes and their values of config
        :return: config object
        """

        class Cfg:
            """
                config class
            """

            def __init__(self, i_dictionary):
                self.database_path = None
                self.session_life = None
                self.__dict__ = i_dictionary

        return Cfg(dictionary)

    cfg_file = open(config_path)
    configuration = {}
    for line in cfg_file:
        field, value = line.split("=")
        configuration[field] = value.rstrip()
    return create(configuration)


path = os.path.dirname(__file__) + ('/' if os.name == "nt" else '')


def open_or_create(db_path: str) -> sqlite3.Connection:
    """

    Creates connection to sql db

    :param db_path: path to db file
    :return: connection
    """
    try:
        valid_path = path + db_path

        connection = sqlite3.Connection(valid_path)

        return connection

    except IOError:

        # если база данных не найдена - завершаем приложение
        print("no db found")
        exit()


if __name__ == "__main__":
    # читаем конфигурацию
    config = read_configuration_file("config.py")

    '''
        парметры конфигурации:
        database_path - путь к базе данных
        auth_database - путь к базе данных аутентификации
        visitation_table - название таблицы да записи посещений
    '''

    # создаем подключение к таблице
    conn = open_or_create(config.database_path)
    cursor = conn.cursor()
    init_sql_handler(config_n=config, cursor_n=cursor, conn_n=conn)

    # Запускаем сервер
    app.run(host="0.0.0.0", port=5000)