from PyQt5.QtWidgets import QComboBox

from Client.test import safe


class QMyComboBox(QComboBox):
    def __init__(self, image_type=None):
        super().__init__()
        if image_type is None:
            self.image_name = "name"
        elif image_type == "lessons":
            self.image_name = "date"
        self.items = {}

    def addItems(self, texts: list) -> None:
        for pair in texts:
            self.items[pair[self.image_name]] = pair
        pass
        super().addItems([i[self.image_name] for i in texts])

    def currentId(self) -> int:
        if self.currentText() == '' or self.currentText() is None or self.currentText() not in self.items.keys():
            raise IndexError()
        return self.items[self.currentText()]["id"]

    def get_data(self):
        return [self.items[key] for key in self.items]

    def clear(self):
        super().clear()
        self.items = {}

    @safe
    def setCurrentMyId(self, ID: int):
        print(self.items)
        for key in self.items:
            if self.items[key]["id"] == ID:
                super().setCurrentText(key)
                return
        raise IndexError("no such id {} in {}".format(ID, self.items))

