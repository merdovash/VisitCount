import datetime

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
        for i, value in enumerate(texts):
            print(i, value)
            self.items[i] = value
        pass
        super().addItems([self._format_name(i[self.image_name]) for i in texts])

    def currentId(self) -> int:
        return self.items[self.currentIndex()]["id"]

    def get_data(self):
        return [self.items[key] for key in self.items]

    def _format_name(self, value):
        if self.image_name == 'date':
            val = datetime.datetime.strptime(value, '%Y-%m-%d %H:%M:%f')
            return val.strftime('%d.%m.%Y %H:%M')
        else:
            return value

    def clear(self):
        super().clear()
        self.items = {}

    @safe
    def setCurrentMyId(self, ID: int):
        print(self.items)
        for i, value in enumerate(self.items):
            if self.items[i]["id"] == ID:
                super().setCurrentIndex(i)
                return
        raise IndexError("no such id {} in {}".format(ID, self.items))
