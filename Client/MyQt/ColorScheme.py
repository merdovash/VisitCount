from PyQt5.QtGui import QColor


class Color:

    @classmethod
    def to_accent(self, color):
        color.setRed(color.red() - 16)
        color.setGreen(color.green() - 16)
        color.setBlue(color.blue() - 16)

        return color

    primary = QColor("#ff8000")

    primary_light = QColor("#ff9933")
    primary_light_accent = QColor("#ef8923")

    primary_dark = QColor("#b25900")

    secondary = QColor("#ebebeb")
    secondary_accent = QColor("#dbdbdb")

    secondary_light = QColor("#efefef")
    secondary_light_accent = QColor("#dfdfdf")

    secondary_dark = QColor("#a4a4a4")

    yellow = QColor("#a4a400")
    yellow_accent = QColor("#b4b400")

    text_color = QColor("#000000")
