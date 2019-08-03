"""
    Server
"""
import os

from flask import Flask, make_response, request, send_file, send_from_directory
from flask_restful import Resource, Api

from Modules import API
from Modules import SourceChecker
from Modules.CabinetLogIn import ServerSide as Cabinet
from Modules.FirstLoad.ServerSide import FirstLoadModule
from Modules.Index import ServerSide as Index
from Modules.Synch.ServerSide import SynchModule
from Modules.VisitLandingPage import ServerSide as VisitLandingPage
from Modules.NewProfessor import ServerSide as NewProfessor
from Modules.UpdateDataViews import ServerSide as GetDataViews
from Parser import Args

path, file = os.path.split(os.path.abspath(__file__))
templates_path = path + "/templates/"

app = Flask(__name__, static_folder=path + "/static", template_folder=path + '/templates')
api = Api(app)

# load modules

SourceChecker.init(app)
Cabinet.init(app)
Index.init(app)
VisitLandingPage.init(app)
NewProfessor.init(app, request)
SynchModule(app, request)
GetDataViews.init(app, request)
API.init(app, request)

FirstLoadModule(app, request)

print(path)


def related(a):
    """

    :param a: related path to file
    :return: full file path
    """
    return os.path.join(path, a)


def page(path, encoding='utf-8'):
    """

    :param encoding:
    :param path:
    :return: complete html page
    """
    with open(path, encoding=encoding) as file:
        return file.read()


@app.route('/TableFilter/<path:file_name>')
def get_TableFilter_lib(file_name):
    return send_file(path + '/TableFilter/' + file_name)


@app.route('/file/<path:file_name>')
def get_resource(file_name):  # pragma: no cover
    """

    :param file_name: path to file in '/templates' for js,htm, html and in '/static' for css
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
    filename, file_extension = os.path.splitext(file_name)

    file_type = file_extension[1:]
    content = ""
    if file_type in ["js"]:
        content = page(path + "/javascript/" + file_name, encoding='utf-8')
    elif file_type in ["css"]:
        content = page(path + "/css/" + file_name, encoding='utf-8')
    elif file_type in ["html", "htm"]:
        content = page(path + "/templates/" + file_name, encoding='utf-8')
    elif file_type in ["gif", "png", "img", 'jpg']:
        content = send_file(path + "/resources/" + file_name, mimetype='image/gif')
    elif file_type == 'exe':
        return send_from_directory(path + "/resources", file_name)

    response = make_response(content)
    response.headers['Content-Type'] = mimetypes.get(file_extension)

    return response


@app.route("/visit", methods=['GET', 'POST'])
def visit():
    """

    :return:
    """
    if request.method == 'GET':
        return page(f'{path}/templates/login2.htm')


# def fix_request_args(args, user_type, user_id):
#     """
#
#     Denies access to private fields
#
#     :param args: request's dict of args
#     :param user_type: type of user access
#     :param user_id: use ID
#     :return: fixed dict of args
#     """
#     request_args = {key: args[key][0] if args[key] is list else args[key] for key in args}
#
#     if str(user_type) == "0":
#         request_args["student_id"] = user_id
#         request_args["user_type"] = 0
#
#     elif str(user_type) == "1":
#         request_args["professor_id"] = user_id
#         request_args["user_type"] = 1
#
#     elif str(user_type) == "2":
#         request_args["admin_id"] = user_id
#         request_args["user_type"] = 2
#
#     return request_args
#
#
# def read_params(args, keys) -> dict:
#     """
#
#     :param args: request's dict of args
#     :param keys: function params
#     :return:
#     """
#     intersect = list(set(keys) & set(args))
#
#     params = {keys[i]: None for i in range(len(keys))}
#
#     for i in range(len(params)):
#         if keys[i] in intersect:
#             params[keys[i]] = args[keys[i]]
#             intersect.remove(keys[i])
#
#     return params
#
#
# @app.route("/get")
# def get_field():
#     """
#
#     1)Запрос должен содержать поля data и uid;
#     2)data может быть любым значением из possible_requests;
#     3)аутентификация по uid;
#     4)uid присваивает значение user_id в своответсвующее поле запроса автоматически,
#     так что невохможно запросить данные для другого пользователя;
#     5)Запрос может содержать дополнительные параметры, необходимые для запроса такие как
#      student_id, professor_id и т.д.
#
#     :return: json string {
#         "type": "get",
#         "status":"OK/ERROR",
#         "message": None if status="OK", "data": get_{$data}
#     }
#     """
#     if request.method == "GET":
#         res = Response("get")
#         if "uid" in request.args:
#             auth_status = db.auth(uid=request.args["uid"])
#             if auth_status:
#
#                 user_type, user_id = auth_status["type"], auth_status["user_id"]
#                 request_args = fix_request_args(request.args, user_type, user_id)
#                 print(request_args)
#                 possible_requests = ["students",
#                                      "professors",
#                                      "disciplines",
#                                      "lessons",
#                                      "groups",
#                                      "visitations",
#                                      "notification_params",
#                                      "table",
#                                      "total",
#                                      "groups_of_total",
#                                      "group_visit"]
#                 if request.args["data"] in possible_requests:
#                     get_func = getattr(db, "get_" + request.args["data"])
#
#                     keys = list(get_func.__code__.co_varnames)
#                     for special in ["self", "request", "params"]:
#                         if special in keys:
#                             keys.remove(special)
#
#                     params = read_params(request_args, keys)
#                     params = tuple(params[key] for key in keys)
#                     print(params)
#
#                     res.set_data(get_func(*params))
#                 else:
#                     res.set_error("field data '{}' is not found".format(request.args["data"]))
#             else:
#                 res.set_error("auth failed")
#         else:
#             res.set_error("missing 'uid' argument")
#
#         return res()


def run():
    """
    run server
    """
    Args('server')
    app.run(host=Args().server_host, port=Args().server_port)
