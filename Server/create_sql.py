"""
   create_sql.py
"""
import random
from datetime import datetime, timedelta
from sql_handler import DataBaseWorker
import config


def load(f:str, spliter:bool):
    o = open(f, encoding="utf-8")
    print(f+" open")
    l = []
    if spliter:
        for line in o:
            l.append(tuple(line.split(" ")))
    else:
        for line in o:
            l.append(line)
    print(f+" open2")
    return l

def recreate(worker):
    def sql_request(message, *args):
        """

        :param message:
        :param args:
        :return:
        """
        return db_worker.sql_request(message, *args)


    def get_date(number):
        """

        :param number:
        :return:
        """
        start_day = datetime(datetime.now().year, 8, 1)
        number_date = start_day + timedelta(
            days=((number % 100 - 1) * 7 + ((number // 100) % 10 - 1) - start_day.weekday()))
        return number_date


    def create_students_table():
        """
            creates students table and fill it
        """
        sql_request(
        """
        CREATE TABLE {}
         (id INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
         last_name VARCHAR(30) character set utf8,
         first_name VARCHAR(30) character set utf8,
         middle_name VARCHAR(30) character set utf8,
         parent_id INTEGER,
         card_id INTEGER);
        """,
                    config.students)
        
        base = "INSERT INTO {} (last_name, first_name, middle_name, card_id) VALUES "
        for i in range(len(students)):
            base += " ('{}','{}','{}',{}),".format(students[i][0], students[i][1],students[i][2], i)
        base = base[:-1]+";"
        sql_request(base, config.students)

        # print(sql_request("SELECT * FROM {}", config.students))


    def create_professors_table():
        """
            creates professors table and fill it
        """
        sql_request("""
                    CREATE TABLE {} (
                        id 		INT NOT NULL AUTO_INCREMENT,
                        last_name 	VARCHAR(30) character set utf8,
                        first_name 	VARCHAR(30) character set utf8,
                        middle_name 	VARCHAR(30) character set utf8,
                        card_id 	INTEGER,
                        PRIMARY KEY (id)
                    );
                    """,
                    config.professors)
        
        base ="INSERT INTO {} (last_name, first_name, middle_name, card_id) VALUES "
        for i in range(len(professors)):
            base += " ('{}', '{}', '{}', {}),".format(professors[i][0],
                                                    professors[i][1],
                                                    professors[i][2],
                                                    i)
        base = base[:-1]+";"
        sql_request(base, config.professors)

        # print("professors: ", sql_request("SELECT * FROM {0}", config.professors))


    def create_groups_table():
        """
            creates groups table and fill it
        """
        sql_request("""CREATE TABLE {} (
                        id INTEGER NOT NULL AUTO_INCREMENT PRIMARY KEY,
                        name VARCHAR(30) character set utf8
                    );
                    """,
                    config.groups)
        base = "INSERT INTO {} (name) VALUES "
        for i in range(len(groups)):
            base+=" ('{}'),".format(groups[i])
        base = base[:-1]+";"
        sql_request(base , config.groups)

        # print("students", sql_request("SELECT * FROM {}", config.groups))


    def create_students_groups_table():
        """
            creates students_groups table and fill it
        """
        sql_request(
        """
        CREATE TABLE {0} (
            student_id INT,
            group_id INT,
            PRIMARY KEY (student_id, group_id)
        );
        """,
        config.students_groups,
        config.students,
        config.groups)
        
        base = "INSERT INTO {} VALUES"
        for i in range(len(groups)):
            student_count = random.randint(10,30)
            start = random.randint(0, len(students))
            delta = random.randint(1, 3)
            for j in range(student_count):
                
                base+=" ({}, {}),".format((start+j*delta)%len(students), i) 
        base = base[:-1]+";"
        sql_request(base, config.students_groups, )

        #print("groups", sql_request("SELECT * FROM {}", config.students_groups))


    def create_disciplines_table():
        """
            creates disciplines table and fill it
        """
        sql_request("""
                    CREATE TABLE {} (
                        id INTEGER NOT NULL AUTO_INCREMENT PRIMARY KEY,
                        name VARCHAR(100) character set utf8
                    );
                    """,
                    config.disciplines)

        for i in range(len(disciplines)):
            sql_request("INSERT INTO {} (name) VALUES ('{}');", config.disciplines, disciplines[i])

        # print("disciplines", sql_request("SELECT * FROM {}", config.disciplines))


    def create_lessons_table():
        """
            creates lessons table and fill it
        """
        sql_request("""
                    CREATE TABLE {0} (
                        id 		INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
                        date 		INT,
                        type 		INT,
                        professor_id 	INT,
                        group_id 	INT,
                        discipline_id 	INT,
                        room_id 	INT,
                        complete 	INT
                    );
                    """,
                    config.lessons,
                    config.professors,
                    config.disciplines,
                    config.groups,
                    config.students_groups,
                    config.rooms)

        res = sql_request("SELECT * FROM {} ORDER BY professor_id", config.notification_params)
        for line in res:
            base = "INSERT INTO {} (date, professor_id, group_id, discipline_id, room_id, complete, type) VALUES"
            professor_id, discipline_id, group_id, max_loss = line
            room_id = 1 + int(random.random() * 200)
            for week in range(1, 18):
                for t in range(3):
                    day = int(random.random() * 6) + 1
                    time = int(random.random() * 5) + 1

                    date = time + 10 * day + week * 100
                    base += " ({}, {}, {}, {}, {}, {}, {}),".format(date,
                                                                        professor_id,
                                                                        group_id,
                                                                        discipline_id,
                                                                        room_id,
                                                                         0 if get_date(date) <= datetime.now() else 1,
                                                                        t)
            base = base[:-1]+";"
            sql_request(base, config.lessons)

        #print("lessons: ",
        #      sql_request("SELECT * FROM {} WHERE group_id=0 AND professor_id=3 AND discipline_id=4", config.lessons))


    def create_notifications_params_table():
        """
            creates notifications params table and fill it
        """
        sql_request("""
                    CREATE TABLE {0} (
                        professor_id 	INT,
                        discipline_id 	INT,
                        group_id 	INT,
                        max_loss 	INT,
                        PRIMARY KEY (professor_id, discipline_id, group_id)
                    );
                    """,
                    config.notification_params,
                    config.professors,
                    config.disciplines,
                    config.groups,
                    config.students_groups)

        for professor_id in range(len(professors)):
            p1 = random.randint(1,7)
            for j in range(1,6):
                discipline = int(j*p1)%len(disciplines)
                p = random.randint(1,17)
                for g in range(1,4):
                    group = int(g*p)%len(groups)
                    sql_request("INSERT INTO {0} (professor_id, discipline_id, group_id, max_loss) VALUES ({1}, {2}, {3}, {4})",
                                config.notification_params,
                                professor_id,
                                discipline,
                                group,
                                3)


    def create_auth_table():
        """
            creates auth table
        """
        sql_request("""
        CREATE TABLE {} (
            id 		INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
            login 	VARCHAR(32) character set utf8,
            password 	VARCHAR(32) character set utf8,
            user_type 	INT,
            user_id 	INT,
            uid 	VARCHAR(50) character set utf8,
            card_id 	INT
        );
        """,
        config.auth)
        p = [["student1", "123456", 0, 11],
        ["[rofessor1","123456", 1, 3],
        ["admin1", "123456", 2, 1]]
        for t in p:
            sql_request("INSERT INTO {0} (login, password, user_type, user_id) VALUES ('{1}','{2}',{3},{4})", t[0],t[1],t[2],t[3])


    def create_notification_table():
        """
            creates notifications table
        """
        sql_request("""
                    CREATE TABLE {} (
                        student_id 	INT,
                        discipline_id 	INT,
                        loss 		INT
		    );
                    """,
                    config.notification)


    def create_visitations_table():
        """
            creates visitations table and fill it
        """
        sql_request(
        """
        CREATE TABLE {0} (
            student_id 	INT,
            id 	INT,
            PRIMARY KEY (student_id, id)
        );
        """,
                    config.visitation,
                    config.students,
                    config.lessons)

        for student in range(len(students)):
            percent = random.random()
            lessons = sql_request("SELECT DISTINCT {0}.id FROM {0} "
                                  "JOIN {1} ON {1}.group_id={0}.group_id "
                                  "JOIN {2} ON {2}.id={1}.student_id "
                                  "WHERE {2}.id={3};",
                                  config.lessons,
                                  config.students_groups,
                                  config.students,
                                  student
                                  )
            base = "INSERT INTO {} VALUES "
            count = 0
            for lesson in lessons:
                if random.random() > percent:
                    base+=" ({}, {}),".format(
                                student,
                                *lesson)
                    count+=1        
            if count>0:
                base = base[:-1]+";"
                print(base[:25])
                sql_request(base, config.visitation)
            print("inserted visitations ", student)


    def create_rooms_table():
        """
            creates rooms table
        """
        sql_request(
        """
        CREATE TABLE {} (
            id INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
            room VARCHAR(30)
        )
        """,
                    config.rooms)


    def create_parents_table():
        """
            creates parents table
        """
        sql_request(
        """
        CREATE TABLE {} (
            id 		INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
            last_name 	VARCHAR(30) character set utf8,
            first_name 	VARCHAR(30) character set utf8,
            middle_name VARCHAR(30) character set utf8,
            email 	VARCHAR(100) character set utf8)
        """,
                    config.parents)

        for parent in parents:
            sql_request("INSERT INTO {} (first_name, last_name, middle_name, email) VALUES ('{}', '{}', '{}', '{}')",
                        config.parents,
                        *parent)
        # print("parents: ", sql_request("SELECT * FROM {}", config.parents))

        # parents and students
        for parent_id in range(len(parents)):
            student_id = random.randint(parent_id, len(students))
            sql_request("UPDATE {0} SET parent_id={1} WHERE id={2}",
                        config.students,
                        parent_id,
                        student_id)


    def create_loss_table():
        """
            creates loss table
        """
        sql_request("CREATE TABLE {} (student_id int)",
                    config.loss)

    db_worker = worker
    students = load("stud.txt", True)
    disciplines = load("disc.txt", False)
    groups = load("group.txt", False)
    professors = load("prof.txt", True)

    if config.db=="mysql":
        c = sql_request("show tables;")
    else:
        c = sql_request("SELECT name from sqlite_master WHERE type='table';")
    print(c)
    for a in c:
        if not a==config.auth:
            sql_request("DROP TABLE {}",*a)

    # студенты

    create_students_table()
    print("stud created")


    # преподаватели

    create_professors_table()
    print("professors created")

    # Группы

    create_groups_table()
    print("groups created")

    create_students_groups_table()
    print("students_groups created")
    # дисциплины

    create_disciplines_table()
    print("disciplines created")
                                
    # параемтры уведомлений
    create_notifications_params_table()
    print("notification created")

    # пары
    create_lessons_table()
    print("lessons created")

    # таблица учетных записей
    create_auth_table()
    print("auth created")

    # таблица посещаемостей
    create_visitations_table()
    print("visitation created")

    # аудитории
    create_rooms_table()

    # родители
    parents = [
        ("Сидоров", "Михаил", "Валентинович", "merd888888@gmail.com"),
        ("Самойлова", "Евгения", "Викторовна", "merd888888@gmail.com"),
        ("Герасимова", "Марина", "Ивановна", "merd888888@gmail.com")
    ]
    create_parents_table()

    print("db created")


if __name__=="__main__":
    import sql_handler
    recreate(sql_handler.DataBaseWorker())
