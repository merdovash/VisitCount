from PyQt5.QtGui import QColor

from Client.Settings import Settings


def bound(number, start, end):
    return min(end, max(start, number))


def color_bound(number):
    return bound(number, 0, 255)


class Color:

    @classmethod
    def to_select(cls, color):
        offset = -30

        c = QColor(color)

        c.setBlue(color_bound(color.blue()*(offset/255+1)))
        c.setGreen(color_bound(color.green()*(offset/255+1)))
        c.setRed(color_bound(color.red()*(offset/255+1)))

        return c

    @classmethod
    def hover(cls, color):
        offset = 30

        c = QColor(color)

        c.setRed(color_bound(color.red()*(offset/255+1)))
        c.setGreen(color_bound(color.green()*(offset/255+1)))
        c.setBlue(color_bound(color.blue()*(offset/255+1)))

        return c

    @classmethod
    def to_accent(cls, color):
        c = QColor(color)

        c.setRed(max(color.red() - 16, 0))
        c.setGreen(max(color.green() - 16, 0))
        c.setBlue(max(color.blue() - 16, 0))

        return c

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
