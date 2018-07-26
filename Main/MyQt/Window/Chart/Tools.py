from Main import config
from Main.DataBase.sql_handler import DataBaseWorker as sql


def get_visit_count(lesson_id):
    return sql.instance().sql_request(
        """
            select count(*)
            from {0}
            join {1} on {0}.id={1}.lesson_id
            where {0}.id={2}
        """,
        config.lessons,
        config.visitation,
        lesson_id
    )[0][0]


def get_student_count(lesson_id):
    return sql.instance().sql_request(
        """
            select count(*) 
            from {0} 
            join {1} on {0}.group_id={1}.group_id 
            where {0}.id={2}
        """,
        config.lessons,
        config.students_groups,
        lesson_id
    )[0][0]
