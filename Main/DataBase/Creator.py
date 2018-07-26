import Main.config as config


def create(cursor):

    if config.db == "sqlite":

        cursor.execute("""
        CREATE TABLE IF NOT EXISTS {} 
            (
                login TEXT PRIMARY KEY,
                password TEXT,
                card_id TEXT,
                user_id INT,
                user_type INT
            );
        """.format(config.auth))

        cursor.execute("""
        CREATE TABLE IF NOT EXISTS {} 
        (
            id INT PRIMARY KEY,
            name TEXT
        );
        """.format(config.disciplines))

        cursor.execute("""
        CREATE TABLE IF NOT EXISTS {}
        (
            id INT PRIMARY KEY,
            name TEXT
        );
        """.format(config.groups))

        cursor.execute("""
        CREATE TABLE IF NOT EXISTS {}
        (
            id INT PRIMARY KEY,
            date TEXT,
            professor_id INT,
            group_id INT,
            discipline_id INT,
            room_id INT,
            completed INT,
            type INT
        );
        """.format(config.lessons))

        cursor.execute("""
        CREATE TABLE IF NOT EXISTS {} (
            `id`	INTEGER NOT NULL UNIQUE,
            `last_name`	TEXT,
            `first_name`	TEXT,
            `middle_name`	TEXT,
            `card_id`	INTEGER,
            `password`	TEXT,
            PRIMARY KEY(`id`)
        );
        """.format(config.professors))

        cursor.execute("""
        CREATE TABLE IF NOT EXISTS {} (
            `id`	INTEGER NOT NULL UNIQUE,
            `last_name`	TEXT,
            `first_name`	TEXT,
            `middle_name`	TEXT,
            `card_id`	INTEGER,
            PRIMARY KEY(`id`)
        );
        """.format(config.students))

        cursor.execute("""
        CREATE TABLE IF NOT EXISTS {} (
            `student_id`	INTEGER,
            `group_id`	INTEGER,
            PRIMARY KEY(`student_id`,`group_id`)
        );
        """.format(config.students_groups))

        cursor.execute("""
        CREATE TABLE IF NOT EXISTS {} (
            `id`	INTEGER,
            `student_id`	INTEGER,
            `synch`	INTEGER
        );
        """.format(config.visitation))
