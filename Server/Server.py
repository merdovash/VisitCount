#!/usr/bin/python3
"""
    Server
"""
import _md5
import json
import os
import random
import sys
from flask import Flask, make_response, request, render_template

from notification import run as notification
from sql_handler import DataBaseWorker
import config

path, file = os.path.split(os.path.abspath(__file__))
templates_path = path + "/templates/"

app = Flask(__name__, static_folder=path + "/static")
db_worker = DataBaseWorker(app)

print(path)


class Response:
    def __init__(self, type):
        self.type = type

    def set_data(self, data):
        self.status = "OK"
        self.data = data
        return self

    def set_error(self, msg):
        self.status = "ERROR"
        self.message = msg
        return self

    def __call__(self, *args, **kwargs):
        return json_create(self.__dict__)


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


@app.route("/super_secret")
def super_secret():
    # import create_sql
    # create_sql.recreate(db_worker)
    pass


@app.route('/file/<path:p>')
def get_resource(p):  # pragma: no cover
    """

    :param p: path to file in '/templates' for js,htm, html and in '/static' for css
    :return: file
    """
    mimetypes = {
        ".css": ["text/css", True],
        ".html": ["text/html", False],
        ".htm": ["text/html", False],
        ".js": ["application/javascript", True],
        ".img": ["image/gif", True],
        ".png": ["image/gif", True],
        ".gif": ["image/gif", True],
    }
    filename, file_extension = os.path.splitext(p)
    mimetype = mimetypes.get(file_extension)
    if mimetype[1]:
        content = open(path + "/static" + "/" + p).read()
    else:
        content = open(templates_path + p).read()
    response = make_response(content)
    response.headers['Content-Type'] = mimetype[0]

    return response


@app.route("/", methods=['GET', 'POST'])
def index():
    """

    :return: index.html
    """
    if request.method == "GET":
        return page("index/index.html", js=True)
    if request.method == "POST":
        data = json_read(request.data.decode('utf8').replace("'", '"'))
        res = Response(data["type"])
        print("from client", data)

        # auth procedure
        if "card_id" in data.keys():
            auth_status = db_worker.auth(card_id=data["card_id"], password=data["password"])
            card_id = data["card_id"]
            by_card = True
        elif "login" in data.keys():
            auth_status = db_worker.auth(login=data["login"], password=data["password"])
            login = data["login"]
            by_card=False
        else:
            return res.set_error("auth fail 2")()

        # main body
        if auth_status:
            if data["type"] == "first":
                # send data for client database
                if by_card:
                    status, r = db_worker.get_data_for_client(professor_card_id=card_id)
                else:
                    status, r = db_worker.get_data_for_client(login=login)

                if status:
                    return res.set_data(r)()
                else:
                    return res.set_error(r)()
            elif data["type"] == "synch":
                # synchronizing client to server
                status, msg = db_worker.synchronize(data["data"])
                if status:
                    notification(db_worker)
                    return res.set_data("")()
                else:
                    return res.set_error(str(msg))()
            elif data["type"] == "notification_params":
                # change all notification params
                professor_id = db_worker.get_professors(card_id=data["card_id"])[0]["id"]
                for change in data["data"]:
                    db_worker.set_notification_params(new_value=change["new_max_loss"],
                                                      professor_id=professor_id,
                                                      discipline_id=change["discipline_id"],
                                                      group_id=change["group_id"])
                return res.set_data("")()
            else:
                return res.set_error("no such type")()
        else:
            return res.set_error("auth failed")()


@app.route("/visit", methods=['GET', 'POST'])
def visit():
    if request.method == 'GET':
        return render_template('index.htm')


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
        db_worker.create_account(login, password, user_id=user_id, account_type=account_type)
        return page("Site/index.html")


def new_uid():
    """

    :return: new unique session id
    """
    number = (random.random() * 100000000000000000) % 13082761331670031
    value = _md5.md5(str(number).encode()).hexdigest()
    while not db_worker.free_uid(value):
        number = (random.random() * 100000000000000000) % 13082761331670031
        value = _md5.md5(str(number).encode()).hexdigest()
    return value


def generate_code():
    value = random.randrange(10000, 100001, 1)
    while len(db_worker.get_telegram_temp(code=value)) != 0:
        value = random.randrange(10000, 100001, 1)
    return value


@app.route("/generateTelegram", methods=["GET"])
def autorizeTelegram():
    response = Response("generateTelegram")
    user_data = db_worker.auth(uid=request.args["uid"])
    if user_data:
        code = generate_code()
        if user_data["telegram"] == "" or user_data["telegram"] == "None":
            response.set_data({"code": code, "connected": False})
        else:
            response.set_data({"code": code, "connected": True})
        db_worker.set_telegram_temp(user_data["id"], code)
    else:
        response.set_error("auth failed")
    return response()


@app.route("/login", methods=["POST"])
def log_in():
    """

    :return: check whether user exist.
    """
    if request.method == "POST":
        res = Response("login")
        login = request.form.get("login")
        password = request.form.get("password")
        user_data = db_worker.auth(login=login, password=password)
        if user_data:
            print(user_data["id"], config.session_life)
            uid = new_uid()
            db_worker.set_session(uid=uid, account_id=user_data["id"])
            return res.set_data(
                {
                    "uid": uid,
                    "user_type": user_data["user_type"],
                    "user": db_worker.get_students(student_id=user_data["id"]) \
                        if str(user_data["user_type"]) == "0" \
                        else db_worker.get_professors(professor_id=user_data["user_id"])
                }
            )()
        else:
            return res.set_error('No such user')()


@app.route("/check_login:<string:login>", methods=["GET"])
def check_login(login):
    """

    :param login: login to check
    :return: is login exist
    """
    if request.method == "GET":
        message = {"answer": None}
        if db_worker.is_login_exist(login):
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
    notification(db_worker)
    return str("")


def fix_request_args(args, user_type, user_id):
    """

    Denies access to private fields

    :param args: request's dict of args
    :param user_type: type of user access
    :param user_id: use ID
    :return: fixed dict of args
    """
    request_args = {key: args[key][0] if args[key] is list else args[key] for key in args}

    if str(user_type) == "0":
        request_args["student_id"] = user_id
        request_args["user_type"] = 0

    elif str(user_type) == "1":
        request_args["professor_id"] = user_id
        request_args["user_type"] = 1

    elif str(user_type) == "2":
        request_args["admin_id"] = user_id
        request_args["user_type"] = 2

    return request_args


def read_params(args, keys) -> dict:
    """

    :param args: request's dict of args
    :param keys: function params
    :return:
    """
    intersect = list(set(keys) & set(args))

    params = {keys[i]: None for i in range(len(keys))}

    for i in range(len(params)):
        if keys[i] in intersect:
            params[keys[i]] = args[keys[i]]
            intersect.remove(keys[i])

    return params


@app.route("/get")
def get_field():
    """

    1)Запрос должен содержать поля data и uid;
    2)data может быть любым значением из possible_requests;
    3)аутентификация по uid;
    4)uid присваивает значение user_id в своответсвующее поле запроса автоматически,
    так что невохможно запросить данные для другого пользователя;
    5)Запрос может содержать дополнительные параметры, необходимые для запроса такие как student_id, professor_id и т.д.

    :return: json string {"type": "get", "status":"OK/ERROR", "message": None if status="OK", "data": get_{$data}}
    """
    if request.method == "GET":
        res = Response("get")
        if "uid" in request.args:
            auth_status = db_worker.auth(uid=request.args["uid"])
            if auth_status:

                user_type, user_id = auth_status["type"], auth_status["user_id"]
                request_args = fix_request_args(request.args, user_type, user_id)
                print(request_args)
                possible_requests = ["students",
                                     "professors",
                                     "disciplines",
                                     "lessons",
                                     "groups",
                                     "visitations",
                                     "notification_params",
                                     "table",
                                     "total",
                                     "groups_of_total"]
                if request.args["data"] in possible_requests:
                    get_func = getattr(db_worker, "get_" + request.args["data"])

                    keys = list(get_func.__code__.co_varnames)
                    for special in ["self", "request", "params"]:
                        keys.remove(special)

                    params = read_params(request_args, keys)
                    params = tuple(params[key] for key in keys)
                    print(params)

                    return res.set_data(get_func(*params))()
                else:
                    return res.set_error("field data '{}' is not found".format(request.args["data"]))()
            else:
                return res.set_error("auth failed")()
        else:
            return res.set_error("missing 'uid' argument")()


@app.route("/table")
def get_table2():
    res = Response("table")
    owner = request.args["owner"]
    student_id = request.args["student_id"]
    discipline_id = request.args["discipline_id"]
    return res.set_data(db_worker.get_table(owner,
                                            student_id=student_id,
                                            discipline_id=discipline_id))()


@app.route("/get_table:<string:uid>:<int:discipline_id>")
def get_table(uid, discipline_id):
    """

    returns all data for table

    :param uid:
    :param discipline_id:
    :return:
    """
    if request.method == "GET":
        user = db_worker.auth(uid=uid)

        response = None

        if user["type"] == 0 or user["type"] == "0":
            student_id = user["id"]
            group = db_worker.get_groups(student_id=student_id)[0]
            data = db_worker.get_data_for_student_table(student_id=student_id, group_id=group["id"],
                                                        discipline_id=discipline_id)

            response = make_response(json_create(data))

        return response


if __name__ == "__main__":
    # читаем конфигурацию

    '''
        парметры конфигурации:
        database_path - путь к базе данных
        auth_database - путь к базе данных аутентификации
        visitation_table - название таблицы да записи посещений
    '''

    # создаем подключение к таблице


    print(db_worker.get_table.__code__.co_varnames)
    # Запускаем сервер
    app.run(host="127.0.0.1", port=5000)
