import datetime


def convert_date(week, day, lesson):
    less = [
        datetime.timedelta(0, 9 * 3600 + 0 * 60),
        datetime.timedelta(0, 10 * 3600 + 45 * 60),
        datetime.timedelta(0, 13 * 3600 + 0 * 60),
        datetime.timedelta(0, 14 * 3600 + 45 * 60),
        datetime.timedelta(0, 16 * 3600 + 20 * 60),
        datetime.timedelta(0, 18 * 3600 + 15 * 60),
    ]
    start = datetime.datetime(2018, 9, 1, 0, 0)
    d = start + datetime.timedelta((week - 1) * 7 + day - 6) + less[lesson - 1]
    normal_date = d.strftime("%d-%m-%Y %I:%M%p")
    return normal_date


if __name__ == "__main__":

    les = [
        [
            (4, 3, (2, 4, 6, 8, 10, 12, 14, 16), 205, 1),
            (4, 4, (1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17), 511, 0),
            (4, 5, (1), 511, 0),
            (4, 5, (2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16), 205, 2),
            (4, 5, (17), 205, 1),
            (6, 4, (3), 205, 1),
            (2, 5, (3), 205, 2)
        ],
        [
            (3, 1, (1, 3, 5, 7, 9, 11, 13, 15, 17), 203, 1),
            (3, 3, (2, 4, 6, 8, 10, 12, 14, 16), 203, 2),
            (3, 4, (2, 4, 6, 8, 10, 12, 14, 16), 203, 2),
            (4, 4, (1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17), 511, 0),
            (4, 5, (1), 511, 0),
            (6, 5, (3), 205, 1)
        ],
        [
            (3, 2, (1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16), 203, 2),
            (3, 2, (17), 203, 1),
            (3, 3, (1, 3, 5, 7, 9, 11, 13, 15, 17), 203, 1),
            (4, 4, (1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17), 511, 0),
            (4, 5, (1), 511, 0),

        ]
    ]

    professor = 1
    discipline = 1
    for i in range(len(les)):
        group = i+1
        for j in range(len(les[i])):
            case = les[i][j]
            day = case[0]
            lesson = case[1]
            room = case[3]
            type_id = case[4]
            if type(case[2]) is tuple:
                for week in list(case[2]):
                    print(
                        "insert into lessons (professor_id, discipline_id, group_id, date, room, type) values ({}, {}, {}, {}, {}, {})".format(
                            professor,
                            discipline,
                            group,
                            convert_date(week, day, lesson),
                            room,
                            type_id
                        ))
            else:
                week = case[2]
                print(
                    "insert into lessons (professor_id, discipline_id, group_id, date, room, type) values ({}, {}, {}, {}, {}, {})".format(
                        professor,
                        discipline,
                        group,
                        convert_date(week, day, lesson),
                        room,
                        type_id
                    ))
