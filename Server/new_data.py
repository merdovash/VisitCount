import datetime

from sql_handler import DataBaseWorker


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


db = DataBaseWorker()

tables = db.sql_request("show tables;")

for t in tables:
    db.sql_request("delete from {0}".format(t[0]))

# students

# group1
db.sql_request("insert into students(last_name, first_name, middle_name) values {}".format(
    ','.join(["('" + "','".join(i.split(' ')) + "')" for i in """
Андреев Дмитрий Алексеевич,
Бабицкий Евгений Михайлович,
Гетманова Мария Дмитриевна,
Головина Изабелла Алексеевна,
Данилова Наталья Александровна,
Захаревич Павел Андреевич,
Иванова Диана Евгеньевна,
Иванова Октябрина Валерьевна,
Лещев Николай Станиславович,
Липкович Денис Вячеславович,
Митусов Алексей Дмитриевич,
Плахтюков Дмитрий Сергеевич,
Поморцев Данила Аркадьевич,
Савельева Наталия Андреевна,
Смирнов Никита Сергеевич,
Цветков Илья Александрович,
Чепчугова Нина Алексеевна,
Чуев Денис Сергеевич,
Шеремет Владимир Александрович,
Шерстобитова Софья Викторовна,
Щербак Владимир Игоревич,
Яковлев Максим Евгеньевич""".replace("\n", "").split(",")])
))

# group2
db.sql_request("insert into students(last_name, first_name, middle_name) values {}".format(
    ','.join(["('" + "','".join(i.split(' ')) + "')" for i in """
Анчишкина Лидия Сергеевна,
Атаманчук Леонтий Сергеевич,
Баев Вадим Дмитриевич,
Галицына Полина Сергеевна,
Гончар Илья Олегович,
Горячева Анна Станиславовна,
Гуляков Ярослав Андреевич,
Жук Дарья Васильевна,
Жуков Семен Павлович,
Игнатьева Анастасия Алексеевна,
Ким  Данил,
Кокарев Денис Андреевич,
Колесников Иван Сергеевич,
Кревлев Максим Дмитриевич,
Лебедева Анастасия Павловна,
Лобазова Ульяна Павловна,
Луканина Анна Васильевна,
Нагорнов Роман Андреевич,
Николаев Валерий Александрович,
Орлова Вероника Алексеевна,
Худайберенов Максим Батырович,
Шунько Анастасия Константиновна
""".replace("\n", "").split(",")])
))

# group3
db.sql_request("insert into students(last_name, first_name, middle_name) values {}".format(
    ','.join(["('" + "','".join(i.split(' ')) + "')" for i in """
Алексеев Андрей Анатольевич,
Андрусович Никита Витальевич,
Базуева Анастасия Олеговна,
Деменева Дарья Александровна,
Друзенко Виктория Валерьевна,
Егоренко Дмитрий Александрович,
Зубин Роман Александрович,
Кирпиченко Дарья Сергеевна,
Козлов Олег Валерьевич,
Корчик Андрей Викторович,
Ксенофонтова Алевтина Дмитриевна,
Лымаренко Александра Руслановна,
Машков Никита Антонович,
Могильный Владислав Анатольевич,
Поленичкина Елизавета Дмитриевна,
Фирсанова Анастасия Александровна,
Хайдари  Джонатан,
Шаронов Никита Максимович,
Шумилова Светлана Игоревна,
Шур Павел Александрович
""".replace("\n", "").split(",")])
))

# students_groups
s_g = [(1, 21), (2, 22), (3, 20)]
for g in range(len(s_g)):
    start = 0 if g == 0 else sum([i[1] for i in s_g[:g]])
    count = s_g[g][1]
    end = start + count

    db.sql_request("insert into students_groups (student_id, group_id) values {}".format(",".join([
        "('" + "','".join([str(i), str(s_g[g][0])]) + "')" for i in range(start, end)])
    ))

# groups
db.sql_request("insert into groups(name) values('ИСТ-621'), ('ИСТ-622'), ('ИСТ-632');")

# disciplines
db.sql_request("insert into disciplines(name) values ('РЗВП');")

# professor
db.sql_request(
    "insert into professors (last_name, first_name, middle_name) values ('Евстигнеев', 'Валерий', 'Александрович')")

# lessons
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
    group = i
    for j in range(len(les[i])):
        case = les[i][j]
        day = case[0]
        lesson = case[1]
        room = case[3]
        type_id = case[4]
        if type(case[2]) is tuple:
            for week in list(case[2]):
                db.sql_request(
                    "insert into lessons (professor_id, discipline_id, group_id, date, room_id, type) values ({}, {}, {}, '{}', {}, {})".format(
                        professor,
                        discipline,
                        group,
                        convert_date(week, day, lesson),
                        room,
                        type_id
                    ))
        else:
            week = case[2]
            db.sql_request(
                "insert into lessons (professor_id, discipline_id, group_id, date, room_id, type) values ({}, {}, {}, '{}', {}, {})".format(
                    professor,
                    discipline,
                    group,
                    convert_date(week, day, lesson),
                    room,
                    type_id
                ))


if __name__ == "__main__":
    pass
