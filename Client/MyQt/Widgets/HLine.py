from PyQt5.QtWidgets import QFrame


class HLine(QFrame):
    def __init__(self, flags=None, *args, **kwargs):
        super().__init__(flags, *args, **kwargs)
        self.setFrameShape(QFrame.HLine)
