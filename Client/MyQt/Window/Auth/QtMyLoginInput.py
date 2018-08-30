from PyQt5 import QtWidgets


class QLoginInput(QtWidgets.QLineEdit):
    def __init__(self):
        super().__init__()
        self.innerText = ""
        self.image = False

    def setText(self, a0: str):
        super().setText(a0)
        self.innerText = a0
        self.image = False

    def set_image_text(self, value: str, image: str):
        super().setText(image)
        self.innerText = str(int(value))
        self.image=True

    def text(self) -> str:
        if self.image:
            return self.innerText
        else:
            return super().text()

    def login(self):
        if self.image:
            return None
        else:
            return super().text()

    def card_id(self):
        if self.image:
            return self.innerText
        else:
            return None
