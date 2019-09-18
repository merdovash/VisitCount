import sys
from pathlib import Path


class _HostConfig:
    address = 'bisitor.itut.ru'


class _HostCLIConfig(_HostConfig):
    def __init__(self):
        import argparse
        parser = argparse.ArgumentParser()
        parser.add_argument('--host-address')

        args, _ = parser.parse_known_args(sys.argv)

        self.address = args.host_address or self.address


class _HostINIConfig(_HostConfig):
    def __init__(self, path):
        import configparser
        config = configparser.ConfigParser()
        print(Path(path).absolute())
        config.read(str(Path(path).absolute()))

        data = config['HOST']

        self.echo = data['address']


def HostClientConfig() -> _HostConfig:
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('--database-config', type=str)

    args, _ = parser.parse_known_args(sys.argv)
    if args.database_config is not None:
        return _HostINIConfig(args.database_path)

    return _HostCLIConfig()

