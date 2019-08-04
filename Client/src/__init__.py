from pathlib import Path


def resource(path: str) -> Path:
    return Path(__file__).with_name(path)