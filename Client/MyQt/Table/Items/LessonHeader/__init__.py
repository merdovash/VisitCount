import datetime
from collections import namedtuple

from Client.IProgram import IProgram
from Client.MyQt.Table.Items.LessonHeader.LessonDateItem import LessonDateItem
from Client.MyQt.Table.Items.LessonHeader.LessonMonthItem import MonthTableItem
from Client.MyQt.Table.Items.LessonHeader.LessonNumberItem import LessonNumberItem
from Client.MyQt.Table.Items.LessonHeader.LessonTypeItem import LessonTypeItem
from Client.MyQt.Table.Items.LessonHeader.LessonWeekDayItem import WeekDayItem
from Client.MyQt.Table.Items.LessonHeader.LessonWeekNumberItem import WeekNumber

LessonHeaderTuple = namedtuple('LessonHeaderTuple', 'month month_day week_number weekday number type')


class LessonHeaderFactory:
    def __init__(self, program: IProgram):
        self.program: IProgram = program

    def create(self, lesson) -> LessonHeaderTuple:
        dt = datetime.datetime.strptime(lesson["date"], self.program['date_format'])

        month_i = MonthTableItem(dt.month)
        date_i = LessonDateItem(dt, lesson["id"], self.program)
        week_number = WeekNumber(dt)
        week_i = WeekDayItem(dt)
        number_i = LessonNumberItem(dt)
        type_i = LessonTypeItem(lesson["type"], self.program)

        return LessonHeaderTuple(month_i, date_i, week_number, week_i, number_i, type_i)
