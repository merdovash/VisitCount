#!/usr/bin/python3
"""
    Server
"""
import _md5
import json
import os
import random
from flask import Flask, make_response, request

from Server.notification import run as notification
from Server.config2 import Config
from Server.Response import Response

from DataBase.Authentication import Authentication
from DataBase.sql_handler import DataBaseWorker

config = Config()

path, file = os.path.split(os.path.abspath(__file__))
templates_path = path + "/templates/"

app = Flask(__name__, static_folder=path + "/static")

db = DataBaseWorker()

print(path)


def related(a):
    """

    :param a: related path to file
    :return: full file path
    """
    return os.path.join(path, a)


def page(p):
    """

    :param p:
    :return: complete html page
    """
    return open(p, encoding='utf-8').read()


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


@app.route("/super_secret")
def super_secret():

    """
    do not uncomment this lines
    """
    # import create_sql
    # create_sql.recreate(db)
    pass


@app.route('/file/<path:p>')
def get_resource(p):  # pragma: no cover
    """

    :param p: path to file in '/templates' for js,htm, html and in '/static' for css
    :return: file
    """
    mimetypes = {
        ".css": "text/css",
        ".html": "text/html",
        ".htm": "text/html",
        ".js": "application/javascript",
        ".img": "image/gif",
        ".png": "image/gif",
        ".gif": "image/gif",
    }
    filename, file_extension = os.path.splitext(p)

    file_type = file_extension[1:]
    content = ""
    if file_type in ["js"]:
        content = page(path + "\\javascript\\" + p)
    elif file_type in ["css"]:
        content = page(path + "\\css\\" + p)
    elif file_type in ["html", "htm"]:
        content = page(path + "\\templates\\" + p)
    elif file_type in ["gif", "png", "img"]:
        content = page(path + "\\resources\\" + p)

    response = make_response(content)
    response.headers['Content-Type'] = mimetypes.get(file_extension)

    return response


@app.route("/", methods=['GET', 'POST'])
def index():
    """

    :return: index.html
    """
    if request.method == "GET":
        return open(path + "\\templates\\index.html", encoding='utf-8').read()
    if request.method == "POST":
        data = json_read(request.data.decode('utf8').replace("'", '"'))
        res = Response(data["type"])

        auth = Authentication(db, config, login=data.get('login'), password=data.get('password'),
                              card_id=data.get('card_id'), uid=data.get('uid'))

        # main body
        if auth.status:
            if data["type"] == "first":
                # send data for client database
                status, r = db.get_data_for_client(professor_card_id=auth.get_user_info()["card_id"])
                if status:
                    return res.set_data(r)()
                else:
                    return res.set_error(r)()
            elif data["type"] == "synch":
                # synchronizing client to server
                status, msg = db.synchronize(data["data"])
                if status:
                    notification(db, config)
                    return res.set_data("")()
                else:
                    return res.set_error(str(msg))()
            elif data["type"] == "notification_params":
                # change all notification params
                professor_id = db.get_professors(card_id=data["card_id"])[0]["id"]
                for change in data["data"]:
                    db.set_notification_params(new_value=change["new_max_loss"],
                                               professor_id=professor_id,
                                               discipline_id=change["discipline_id"],
                                               group_id=change["group_id"])
                return res.set_data("")()
            else:
                return res.set_error("no such type")()
        else:
            return res.set_error("auth failed")()


@app.route("/update", methods=["POST"])
def update_local_database():
    """
    work on update local database request

    :return type: Response()
    :return:
    """
    if request.method == "POST":
        data = json_read(request.data.decode('utf8').replace("'", '"'))
        auth = Authentication(db, config,
                              login=data.get('login'),
                              password=data.get('password'),
                              card_id=data.get('card_id'),
                              uid=data.get('uid'))
        res = Response('update')
        if auth.status:
            if auth.user_type == 1:
                res.set_data(db.get_updates(auth.user_id))
            else:
                res.set_error("no such privileges")
        else:
            res.set_error("auth failed")

        return res()


@app.route("/visit", methods=['GET', 'POST'])
def visit():
    """

    :return:
    """
    if request.method == 'GET':
        return page(f'{path}\\templates\\visit.htm')


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
        db.create_account(login, password, user_id=user_id, account_type=account_type)
        return page("Site/index.html")


def new_uid():
    """

    :return: new unique session id
    """
    number = (random.random() * 100000000000000000) % 13082761331670031
    value = _md5.md5(str(number).encode()).hexdigest()
    while not db.free_uid(value):
        number = (random.random() * 100000000000000000) % 13082761331670031
        value = _md5.md5(str(number).encode()).hexdigest()
    return value


@app.route("/login", methods=["POST"])
def log_in():
    """

    :return: check whether user exist.
    """
    res = Response("login")
    if request.method == "POST":
        login = request.form.get("login")
        password = request.form.get("password")
        auth = Authentication(db, config, login=login, password=password)
        if auth.status:
            user_data = auth.get_user_info()
            print(user_data["id"], config.session_life)
            uid = new_uid()
            db.set_session(uid=uid, account_id=user_data["id"])
            res.set_data(
                {
                    "uid": uid,
                    "user_type": user_data["user_type"],
                    "user": db.get_students(student_id=user_data["id"]) if str(user_data["user_type"]) == "0" else db.get_professors(professor_id=user_data["user_id"])
                }
            )
        else:
            res.set_error(auth.error)
    else:
        res.set_error("access denied")
    return res()


@app.route("/notification")
def note():
    """

    This function execute only for tests
    Real usage should be automatic

    :return: data of loss
    """
    notification(db, config)
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
            auth_status = db.auth(uid=request.args["uid"])
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
                    get_func = getattr(db, "get_" + request.args["data"])

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


def run():
    """
    run server
    """
    app.run(host="127.0.0.1", port=5000)
