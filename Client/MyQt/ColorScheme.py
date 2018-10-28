from PyQt5.QtGui import QColor


class Color:

    @classmethod
    def hover(cls, color):
        c = QColor(color)

        c.setRed(min(color.red() + 16, 255))
        c.setGreen(min(color.green() + 16, 255))
        c.setBlue(min(color.blue() + 16, 255))

        return c

    @classmethod
    def to_accent(cls, color):
        color.setRed(max(color.red() - 16, 0))
        color.setGreen(max(color.green() - 16, 0))
        color.setBlue(max(color.blue() - 16, 0))

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
