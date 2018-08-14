import datetime

less = [
    datetime.timedelta(0, 9 * 3600 + 0 * 60),
    datetime.timedelta(0, 10 * 3600 + 45 * 60),
    datetime.timedelta(0, 13 * 3600 + 0 * 60),
    datetime.timedelta(0, 14 * 3600 + 45 * 60),
    datetime.timedelta(0, 16 * 3600 + 20 * 60),
    datetime.timedelta(0, 18 * 3600 + 15 * 60),
]


def from_index_to_time(index):
    return less[index]


def from_time_to_index(time: datetime.datetime):
    if time.hour == 9:
        return 1
    elif time.hour == 10:
        return 2
    elif time.hour == 13:
        return 3
    elif time.hour == 14:
        return 4
    elif time.hour == 16:
        return 5
    elif time.hour == 18:
        return 6
    else:
        return -1
