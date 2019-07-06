import logging

from Parser import Args


def init():
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s', datefmt='%Y-%m-%d %H:%M:%S')

    server_logger = logging.getLogger("server")
    server_logger.setLevel(logging.ERROR)
    server_fh = logging.FileHandler('server.log')
    server_fh.setLevel(logging.INFO)
    server_logger.addHandler(server_fh)

    auto_notification_logger = logging.getLogger("notification")
    auto_notification_logger.setLevel(Args().logging_level)
    auto_fh = logging.FileHandler("auto_notification.log")
    auto_fh.setLevel(logging.DEBUG)
    auto_fh.setFormatter(formatter)
    auto_notification_logger.addHandler(auto_fh)