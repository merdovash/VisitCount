import argparse
import sys


class ServerConfig:
    def __init__(self):
        parser = argparse.ArgumentParser()
        parser.add_argument('--server-host', type=str, dest='server_host', default='0.0.0.0')
        parser.add_argument('--server-port', type=str, dest='server_port', default='5000')

        res, _ = parser.parse_known_args(sys.argv)

        self.host = res.server_host
        self.port = res.server_port

    def address(self):
        res = self.host
        if self.port:
            res += f':{self.port}'

        return res