from DataBase.ClentDataBase import ClientDataBase


def get_visit_count(db:ClientDataBase, lesson_id):
    return db.sql_request(
        """
            select count(*)
            from {0}
            join {1} on {0}.id={1}.lesson_id
            where {0}.id={2}
        """,
        ClientDataBase.Schema.lessons.name,
        ClientDataBase.Schema.visitations.name,
        lesson_id
    )[0][0]


def get_student_count(db:ClientDataBase, lesson_id):
    return db.sql_request(
        """
            select count(*) 
            from {0} 
            join {1} on {0}.group_id={1}.group_id 
            where {0}.id={2}
        """,
        ClientDataBase.Schema.lessons.name,
        ClientDataBase.Schema.students_groups.name,
        lesson_id
    )[0][0]
