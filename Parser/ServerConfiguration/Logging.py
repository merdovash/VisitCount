import argparse
import sys


class LoggingConfig():
    def __init__(self):
        import logging
        parser = argparse.ArgumentParser()
        parser.add_argument('--logging-level', metavar="select logging level", default=logging.INFO, type=int)

        res, _ = parser.parse_known_args(sys.argv)

        self.level = res.logging_level