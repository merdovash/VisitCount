import json

from requests import post

from Main import config
from Main.Types import Status, Response


class Server:
    @staticmethod
    def send(request: str, data: dict, onResponse: callable = lambda x: 0, onError:callable = lambda x:0):
        try:
            r = post(url=config.server + request,
                     headers={"Content-Type": "application/json"},
                     data=json.dumps(data))

            res_status = Status(r.text)
            if res_status == Response.JSON:
                res = json.loads(r.text)
                if res["type"] == data["type"]:
                    if res["status"] == "OK":
                        onResponse(res["data"])
                    else:
                        onError(res["message"])
                else:
                    onError(res["message"])
            else:
                onError(r.status_code)
        except Exception as e:
            print(e)
