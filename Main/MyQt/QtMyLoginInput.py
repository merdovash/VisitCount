from PyQt5 import QtWidgets


class QLoginInput(QtWidgets.QLineEdit):
    def __init__(self):
        super().__init__()
        self.innerText = ""

    def setText(self, a0: str):
        super().setText(a0)
        self.innerText = a0

    def set_image_text(self, value: str, image: str):
        super().setText(image)
        self.innerText = str(int(value))

    def text(self) -> str:
        return self.innerText
