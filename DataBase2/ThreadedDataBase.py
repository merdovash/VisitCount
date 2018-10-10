from queue import Queue
from threading import Thread


class DataBase(Thread):
    def __init__(self):

        super().__init__()

        self.session = None

        self.queue = Queue()

    def add_request(self, func):
        self.queue.put(func)

    def run(self):
        from DataBase2 import session
        self.session = session

        while True:
            if not self.queue.empty():
                func = self.queue.get()

                func(self.session)


def test():
    pass
