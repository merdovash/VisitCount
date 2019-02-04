from PyQt5.QtCore import QThread


class SimpleThread(QThread):
    def __init__(self, func):
        super().__init__()
        self.func = func

    def run(self):
        self.func(*self.args, **self.kwargs)

    def __call__(self, *args, **kwargs):
        self.args = args
        self.kwargs = kwargs

        self.start()
