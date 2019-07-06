#!/usr/bin/python3
"""
    run
"""

from Parser import Args

Args('server')

if __name__ == "__main__":
    from threading import Thread
    import BisitorLogger.server
    import Server.Server as Server
    from Modules import AutoNotification

    BisitorLogger.server.init()

    server_thread = Thread(target=Server.run)
    notification_thread = Thread(target=AutoNotification.init)
    server_thread.start()
    notification_thread.start()
