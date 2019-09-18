import sys
from pathlib import Path


class _DatabaseConfig:
    echo = False


class _DatabaseINIConfig(_DatabaseConfig):
    def __init__(self, path):
        import configparser
        config = configparser.ConfigParser()
        print(Path(path).absolute())
        config.read(str(Path(path).absolute()))

        data = config['DATABASE']

        self.echo = bool(data['echo'])


class _DatabaseCLIConfig(_DatabaseConfig):
    def __init__(self):
        import argparse
        parser = argparse.ArgumentParser()
        parser.add_argument('--database-echo', type=str)

        args, _ = parser.parse_known_args(sys.argv)

        self.echo = bool(args.database_echo) or self.echo


def DatabaseClientConfig() -> _DatabaseConfig:
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('--database-config', type=str)

    args, _ = parser.parse_known_args(sys.argv)
    if args.database_config is not None:
        return _DatabaseINIConfig(args.database_path)

    return _DatabaseCLIConfig()