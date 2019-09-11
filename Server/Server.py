"""
    Server
"""
import os

from flask import Flask, make_response, request, send_file, send_from_directory

from Modules import API
from Modules.FirstLoad.ServerSide import FirstLoadModule
from Modules.Synch.ServerSide import SynchModule
from Modules.NewProfessor import ServerSide as NewProfessor
from Modules.UpdateDataViews import ServerSide as GetDataViews
from Parser import Args

path, file = os.path.split(os.path.abspath(__file__))
templates_path = path + "/templates/"

app = Flask(__name__, static_folder=path + "/static", template_folder=path + '/templates')

# load modules

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


def page(file_path, encoding='utf-8'):
    """

    :param encoding:
    :param file_path:
    :return: complete html page
    """
    with open(file_path, encoding=encoding) as f:
        return f.read()


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


def run():
    """
    run server
    """
    Args('server')
    app.run(host=Args().server.host, port=Args().server.port)
