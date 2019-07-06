import datetime


def find(func, l, default=None):
    res = list(filter(func, l))
    if len(res) > 0:
        return res[0]
    else:
        return default


def closest_lesson(lessons: list, date_format="%d-%m-%Y %I:%M%p"):
    """

    :param date_format:
    :param lessons: list of lessons
    :return: closest lesson in list to current datetime
    """
    if len(lessons) == 0:
        return None
    closest = min(
        lessons,
        key=lambda x: abs(datetime.datetime.now() - x.date))
    return closest