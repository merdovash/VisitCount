from datetime import datetime, timedelta

START_STUDY = datetime(2008, 9, 1)


def semester_start():
    now = datetime.now()
    year = now.year
    month = now.month

    if month > 6:
        return datetime(year, 9, 1)
    else:
        temp = datetime(year, 2, 7)
        temp += timedelta(7 - temp.weekday())
        return temp


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


def study_semester(date: datetime):
    days = (date - START_STUDY).days
    semester = 1
    while days > 0:
        days -= 153 if semester % 2 else 212.25
        semester += 1

    return semester


class BisitorDateTime(datetime):
    def __new__(cls, *args, **kwargs):
        datetime.__new__(cls, *args, **kwargs)

    _semester = None

    @property
    def semester(self):
        def define_semester():
            days = (self - START_STUDY).days
            semester = 1
            while days > 0:
                days -= 153 if semester % 2 else 212.25
                semester += 1

            return semester

        if self._semester is None:
            self._semester = define_semester()
        return self._semester

    _week = None

    @property
    def week(self):
        def define_week():
            month = self.month
            if month < 2 or (month == 2 and self.day - self.weekday() < 0):
                return week(self) + (week(datetime(self.year - 1, 12, 31)) - week(datetime(self.year - 1, 9, 1))) + 1

            elif 2 <= month < 9:
                start_date = datetime(self.year, 2, 4)
                while start_date.weekday() != 1:
                    start_date += timedelta(1)
                return week(self) - week(start_date) + 1

            else:
                start_date = datetime(self.year - 1, 9, 1)
                if month > 9 or start_date.weekday() <= 6:
                    return week(self) - week(start_date) + 1
                else:
                    return week(self) - week(start_date)

        if self._week is None:
            self._week = define_week()
        return self._week

    @property
    def weekday(self):
        return datetime.weekday(self)
