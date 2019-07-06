#!/usr/bin/python3
"""
    run
"""
from threading import Thread

import BisitorLogger.server
import Server.Server as Server
from Modules import AutoNotification
from Parser import Args

if __name__ == "__main__":
    Args('server')
    BisitorLogger.server.init()

    server_thread = Thread(target=Server.run)
    notification_thread = Thread(target=AutoNotification.init)
    server_thread.start()
    notification_thread.start()
