from datetime import datetime, timedelta


def week(date: datetime = datetime.now()) -> int:
    return date.isocalendar()[1]


def study_week(date: datetime = datetime.now()) -> int:
    month = date.month
    if month < 2 or (month == 2 and date.day - date.weekday() < 0):
        return week(date) + (week(datetime(date.year - 1, 12, 31)) - week(datetime(date.year - 1, 9, 1))) + 1

    elif 2 <= month < 9:
        start_date = datetime(date.year, 2, 7)
        while start_date.weekday() != 1:
            start_date += timedelta(1)
        return week(date) - week(start_date) + 1

    else:
        start_date = datetime(date.year - 1, 9, 1)
        if month > 9 or start_date.weekday() <= 6:
            return week(date) - week(start_date) + 1
        else:
            return week(date) - week(start_date)