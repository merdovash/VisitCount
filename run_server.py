#!/usr/bin/python3
"""
    run
"""
import argparse
import logging
import sys
from threading import Thread

import BisitorLogger
import Server.Server as Server
from Modules import AutoNotification

if __name__ == "__main__":
    from Parser.server import server_args

    BisitorLogger.init()

    server_thread = Thread(target=Server.run)
    notification_thread = Thread(target=AutoNotification.init)
    server_thread.start()
    notification_thread.start()
