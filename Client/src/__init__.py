import json
from pathlib import Path


def resource(path: str) -> Path:
    return Path(__file__).with_name(path)


def load_resource(path: str, mode='r') -> str or bytes:
    post_process = lambda x: x

    if mode == 'json':
        post_process = lambda x: json.loads(x)
        mode = 'r'

    with open(str(resource(path)), mode, encoding="utf-8") as resource_file:
        return post_process(resource_file.read())
