from PyQt5.QtCore import QRunnable


class SimpleRunnable(QRunnable):
    def __init__(self, func):
        super().__init__()

        self.func = func

    def run(self):
        try:
            self.func(*self.args, **self.kwargs)
        except:
            raise

    def __call__(self, *args, **kwargs):
        self.args = args
        self.kwargs = kwargs

        self.run()
