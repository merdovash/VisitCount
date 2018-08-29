from typing import List, Dict, Any

from DataBase.sql_handler import DataBase, and_or_where


class DataBaseWorker(DataBase):
    """
    class
    """

    def is_login_exist(self, login_name):
        """

        Check whether login is already exist or not.

        :param login_name: login
        :return: bool
        """
        res = self.sql_request("SELECT COUNT(login) FROM {0} WHERE login='{1}'",
                               DataBase.Schema.auth.name,
                               login_name)

        results_count = len(res)
        return results_count > 0

    def create_account(self, login, password, account_type=None, user_id=None):
        # TODO: hash function to password
        """

        Creates new account by inserting new line into sql table.

        :param login: login of new user
        :param password: password of new user
        :param account_type: type of new account [0:student, 1:professor]
        :param user_id: ID of student or professor
        """
        if account_type is None:
            account_type = 0
        if user_id is None:
            user_id = 0
        self.sql_request("INSERT INTO {} (login,password,user_type,user_id) VALUES  ('{}','{}',{},{})",
                         DataBase.Schema.auth.name,
                         login,
                         password, account_type, user_id)

    def auth(self, login=None, password=None, uid=None, card_id=None):
        # TODO: hash to function password
        """

        Process of authentication

        :param card_id: you can auth with card id + password
        :param login: login of user
        :param password: password of user
        :param uid: session ID
        :return: bool
        """
        if (login is not None or card_id is not None) and password is not None:
            if login is not None:
                res = self.sql_request("SELECT id, user_type, user_id FROM {0} WHERE login='{1}' AND password='{2}';",
                                       DataBase.Schema.auth.name,
                                       login,
                                       password)
                if len(res) > 0:
                    return {"id": res[0][0],
                            "user_type": res[0][1],
                            "user_id": res[0][2]}
                else:
                    return False
            elif card_id is not None:
                res = self.sql_request("SELECT id FROM {0} WHERE card_id='{1}' AND password='{2}';",
                                       DataBase.Schema.auth.name,
                                       card_id,
                                       password)
                if len(res) > 0:
                    return {"id": res[0][0]}
                else:
                    return False

        elif uid is not None:
            res = self.sql_request("SELECT user_type, user_id, id FROM {0} WHERE uid='{1}';",
                                   DataBase.Schema.auth.name,
                                   uid)

            if res:
                return {
                    "type": res[0][0],
                    "user_id": res[0][1],
                    "id": res[0][2]
                }
            else:
                return False

    def get_students_groups(self, professor_id=None) -> object:
        """

        :param professor_id: ID of professor
        :return: data of table students_groups
        """
        request = "SELECT DISTINCT {0}.student_id, {0}.group_id FROM {0} "
        params = [DataBase.Schema.students_groups.name]

        if professor_id is not None:
            request += "JOIN {1} ON {1}.group_id={0}.group_id " \
                       "WHERE {1}.professor_id={2} "
            params.extend([DataBase.Schema.lessons.name, professor_id])

            res = self.sql_request(request, *tuple(params))
            return [{'student_id': str(res[i][0]), 'group_id': str(res[i][1])} for i in range(len(res))]
        else:
            return None

    def get_auth_info(self, professor_id: int or str) -> List[Dict[str, Any]]:
        req = "SELECT login, password, card_id, user_id, user_type FROM {0} WHERE user_type=1 AND user_id={1}"
        params = [DataBase.Schema.auth.name, professor_id]
        res = [{"login": i[0],
                "password": i[1],
                "card_id": i[2],
                "user_id": i[3],
                "user_type": i[4]} for i in self.sql_request(req, *tuple(params))]
        return res

    def get_data_for_client(self, professor_id) -> Dict[str, List[Dict[str, str or int]]]:
        """

        :param professor_id: returns data for professor by his id
        :return: complete data for client for first connection
        """

        return {
            DataBase.Schema.professors.name: self.get_professors(professor_id=professor_id),
            DataBase.Schema.disciplines.name: self.get_disciplines(professor_id=professor_id),
            DataBase.Schema.lessons.name: self.get_lessons(professor_id=professor_id),
            DataBase.Schema.groups.name: self.get_groups(professor_id=professor_id),
            DataBase.Schema.students.name: self.get_students(professor_id=professor_id),
            DataBase.Schema.students_groups.name: self.get_students_groups(professor_id=professor_id),
            DataBase.Schema.visitations.name: self.get_visitations(professor_id=professor_id),
            DataBase.Schema.auth.name: self.get_auth_info(professor_id)
        }

    def free_uid(self, value) -> bool:
        """

        Check whether session ID is free to set to new session.

        :param value: session ID
        :return: bool
        """
        res = self.sql_request("SELECT * FROM {} "
                               "WHERE uid='{}'",
                               DataBase.Schema.auth.name,
                               value)
        return len(res) == 0

    def set_session(self, uid: str, account_id: int or str):
        """

        Set session id to some account

        :param uid: free session ID
        :param account_id: account ID
        """
        self.sql_request("""
            UPDATE {0}
            SET uid='{1}'
            WHERE id={2}
        """,
                         DataBase.Schema.auth.name,
                         uid,
                         account_id)

    def get_parent(self, student_id=None) -> dict:
        """

        :param student_id: students ID of parent's child
        :return: dictionary of full parent information
        """
        request = "SELECT email, first_name, last_name, middle_name FROM {0} " \
                  "JOIN {1} ON {0}.id={1}.parent_id " \
                  "WHERE {1}.student_id={2}"
        params = [DataBase.Schema.parents.name,
                  DataBase.Schema.parents_students.name,
                  student_id]
        res = self.sql_request(request, *tuple(params))
        if len(res) == 0:
            raise Exception("Parent for student <student_id={}> is not registered".format(student_id))
        return {"email": res[0][0],
                "name": "{} {} {}".format(res[0][1], res[0][2], res[0][3])}

    def set_request_params(self, request: str, params: list, param, string: str, size: int):
        """

        :param request: request string
        :param params: list of format params of request
        :param param: new parameter
        :param string: name of parameter
        :param size: maximum count of params that allows not to set 'AND' keyword
        :return: new request and new params
        """
        if param is not None:
            request += and_or_where(params, size)
            request += string
            params.append(param)
        return request, params

    def get_professors(self, professor_id=None, card_id=None, group_id=None, discipline_id=None,
                       student_id=None) -> list:
        """

        :param student_id: you select professors by student
        :param discipline_id: you can select professors by discipline
        :param group_id: you can select professors by  group
        :param card_id: you can select professor by card id
        :param professor_id: you can select professor by id
        :return: Last Name, First Name, Middle Name as Dictionary
        """

        request = "SELECT {0}.first_name, {0}.last_name, {0}.middle_name, {0}.id, {0}.card_id FROM {0} "
        params = [DataBase.Schema.professors.name]
        if group_id is not None or discipline_id is not None or student_id is not None:
            request += "JOIN {1} ON {0}.id={1}.professor_id "
            params.append(DataBase.Schema.lessons.name)
            if student_id is not None:
                request += "JOIN {2} ON {1}.group_id={2}.group_id "
                params.append(DataBase.Schema.students_groups.name)
                request += and_or_where(params, 3)
                request += "{2}.student_id={" + str(len(params)) + "} "
            request, params = self.set_request_params(request, params, group_id,
                                                      "{1}.group_id={" + str(len(params)) + "} ", 2)
            request, params = self.set_request_params(request, params, discipline_id,
                                                      "{1}.discipline_id={" + str(len(params)) + "} ", 2)
        request, params = self.set_request_params(request, params, professor_id, "{0}.id={" + str(len(params)) + "} ",
                                                  1)
        request, params = self.set_request_params(request, params, card_id, "{0}.card_id={" + str(len(params)) + "} ",
                                                  1)

        return [
            {
                "first_name": res[0],
                "last_name": res[1],
                "middle_name": res[2],
                "id": str(res[3]),
                "card_id": str(res[4])
            }
            for res in self.sql_request(request, *tuple(params))
        ]

    def get_student_name(self, student_id: int or str) -> str:
        """

        :param student_id: student ID
        :return: Full name of student as a String
        """
        res = self.get_students(student_id=student_id)
        return res[0]["last_name"] + " " + res[0]["first_name"] + " " + res[0]["middle_name"]

    def get_group_visit(self, professor_id=None, *args):
        dates = [{'id': i, 'name': i} for i in range(18)]
        rows = [{'id': i[0], 'name': i[1]} for i in self.sql_request("""
        SELECT {0}.id, {0}.name 
        FROM {0} 
        JOIN {1} ON {0}.id={1}.group_id
        WHERE {1}.professor_id={2}""",
                                                                     DataBase.Schema.groups.name,
                                                                     DataBase.Schema.lessons.name,
                                                                     professor_id)]
        visit = [[i[2], i[1], i[0]] for i in self.sql_request("""
        SELECT count({1}.lesson_id)/count({0}.id), {1}.group_id, WEEK({0}.date) as 'week' 
        FROM {0}
        JOIN {1} ON {1}.lesson_id={0}.id
        LEFT JOIN {2} ON {2}.student_id={1}.student_id AND {1}.lesson_id={0].id
        WHERE {0}.professor_id={3}
        GROUP BY {0}.group_id, week""",
                                                              DataBase.Schema.visitations.name,
                                                              DataBase.Schema.lessons.name,
                                                              DataBase.Schema.students_groups.name,
                                                              professor_id)]

        return {
            'dates': dates,
            'rows': rows,
            'visit': visit
        }

    def get_groups(self, professor_id=None, discipline_id=None, student_id=None, group_id=None) -> list:
        """

        :param group_id: you can select groups by id
        :param student_id: you can select groups by student
        :param professor_id: you can select groups by professor
        :param discipline_id: you can select groups by discipline
        :return: data of {"name": res[i][name], "id": res[i][id]}
        """
        request = "SELECT DISTINCT {0}.id, {0}.name FROM {0} "
        params = [DataBase.Schema.groups.name]

        if professor_id is not None or discipline_id is not None or student_id is not None:
            request += "JOIN {1} ON {1}.group_id={0}.id "
            params.append(DataBase.Schema.lessons.name)
            if student_id is not None:
                request += "JOIN {2} ON {2}.group_id ={1}.group_id "
                params.append(DataBase.Schema.students_groups.name)
                request += and_or_where(params, 2)
                request += "{2}.student_id={" + str(len(params)) + "} "
                params.append(student_id)
            request, params = self.set_request_params(request, params, professor_id,
                                                      "{1}.professor_id={" + str(len(params)) + "} ", 2)
            request, params = self.set_request_params(request, params, discipline_id,
                                                      "{1}.discipline_id={" + str(len(params)) + "} ", 2)
        request, params = self.set_request_params(request, params, group_id, "{0}.id={" + str(len(params)) + "}", 2)

        return [
            {
                "name": res[1],
                "id": str(res[0])
            }
            for res in self.sql_request(request, *tuple(params))
        ]

    def get_disciplines(self, student_id=None, professor_id=None, discipline_id=None, group_id=None) -> list:
        """

        :param group_id: you can select disciplines by group
        :param discipline_id: you can select disciplines by id
        :param professor_id: you can select disciplines by professor
        :param student_id: you can select disciplines by student
        :return: data of disciplines
        """

        request = "SELECT DISTINCT {0}.id, {0}.name FROM {0} " \
                  "JOIN {1} ON {0}.id={1}.discipline_id "
        params = [DataBase.Schema.disciplines.name, DataBase.Schema.lessons.name]
        if student_id is not None:
            request += "JOIN {2} ON {1}.group_id={2}.group_id " \
                       "WHERE {2}.student_id={3}"
            params.extend([DataBase.Schema.students_groups.name, student_id])
        request, params = self.set_request_params(request, params, professor_id,
                                                  "{1}.professor_id={" + str(len(params)) + "} ",
                                                  2)
        request, params = self.set_request_params(request, params, discipline_id, "{0}.id={" + str(len(params)) + "} ",
                                                  2)
        request, params = self.set_request_params(request, params, group_id, "{1}.group_id={" + str(len(params)) + "} ",
                                                  2)

        return [
            {
                "name": res[1],
                "id": str(res[0])
            }
            for res in self.sql_request(request, *tuple(params))
        ]

    def get_students(self, group_id=None, student_list=None, professor_id=None, student_id=None, card_id=None) -> list:
        """

        :param student_id: you can select students by id
        :param group_id: you can select students by group
        :param student_list: you can select students by data if id
        :param professor_id: you can select students by professor
        :return: data of students  keys=(id, last_name, first_name, middle_name, card_id)
        """
        request = "SELECT DISTINCT {0}.id, {0}.first_name, {0}.last_name, {0}.middle_name, {0}.card_id " \
                  "FROM {0} "
        params = [DataBase.Schema.students.name]

        if group_id is not None or professor_id is not None:
            request += "JOIN {1} ON {1}.student_id={0}.id " \
                       "JOIN {2} ON {2}.group_id={1}.group_id "
            params.extend([DataBase.Schema.students_groups.name, DataBase.Schema.lessons.name])
            request, params = self.set_request_params(request, params, professor_id,
                                                      "{2}.professor_id={" + str(len(params)) + "} ", 3)
            request, params = self.set_request_params(request, params, group_id,
                                                      "{1}.group_id={" + str(len(params)) + "} ", 3)
        request, params = self.set_request_params(request, params, student_list,
                                                  "{0}.id IN {" + str(len(params)) + "} ", 1)
        request, params = self.set_request_params(request, params, student_id, "{0}.id={" + str(len(params)) + "} ", 1)
        request, params = self.set_request_params(request, params, card_id, "{0}.card_id={" + str(len(params)) + "} ",
                                                  1)

        return [
            {
                "id": str(res[0]),
                "last_name": res[2],
                "first_name": res[1],
                "middle_name": res[3],
                "card_id": str(res[4])
            }
            for res in self.sql_request(request, *tuple(params))]

    def get_lessons(self, group_id=None, professor_id=None, discipline_id=None, student_id=None,
                    lesson_id=None, completed=None) -> list:
        """

        :param lesson_id: you can select lessons by id
        :param student_id: you can select lessons by student
        :param group_id: you can select lessons by group
        :param professor_id: you can select lessons by professor
        :param discipline_id: you can select lessons by discipline
        :param completed:  you can select lessons by completed status
        :return: data of lessons
        """
        request = "SELECT DISTINCT {0}.id, {0}.date, {0}.room_id, {0}.group_id, {0}.discipline_id, {0}.professor_id," \
                  " {0}.completed, {0}.type FROM {0} "
        params = [DataBase.Schema.lessons.name]
        if student_id is not None:
            request += "JOIN {1} ON {0}.group_id={1}.group_id "
            params.append(DataBase.Schema.students_groups.name)
            request += and_or_where(params, 2)
            request += "{1}.student_id={" + str(len(params)) + "} "
            params.append(student_id)
        request, params = self.set_request_params(request, params, group_id, "{0}.group_id={" + str(len(params)) + "} ",
                                                  1)
        request, params = self.set_request_params(request, params, professor_id,
                                                  "{0}.professor_id={" + str(len(params)) + "} ",
                                                  1)
        request, params = self.set_request_params(request, params, discipline_id,
                                                  "{0}.discipline_id={" + str(len(params)) + "} ",
                                                  1)
        request, params = self.set_request_params(request, params, lesson_id, "{0}.id={" + str(len(params)) + "} ", 1)
        request, params = self.set_request_params(request, params, completed,
                                                  "{0}.completed={" + str(len(params)) + "} ", 1)

        request += "ORDER BY {0}.date "

        return [
            {
                'id': str(res[0]),
                'date': str(res[1]),
                'room_id': str(res[2]),
                'group_id': str(res[3]),
                'discipline_id': str(res[4]),
                'professor_id': str(res[5]),
                'type': str(res[7]),
                'completed': res[6]
            } for res in self.sql_request(request, *tuple(params))]

    def get_visitations(self, group_id=None, professor_id=None, discipline_id=None,
                        student_list=None, student_id=None, synch=None) -> list:
        """

        :param synch: you can select visitation by synch status
        :param student_id: you can select visitations by student
        :param group_id: you can select visitations by group
        :param professor_id: you can select visitations by professor
        :param discipline_id: you can select visitations by discipline
        :param student_list: you can select visitations by student data
        :return:
        """
        request = "SELECT DISTINCT {0}.student_id, {0}.lesson_id FROM {0} "
        params = [DataBase.Schema.visitations.name]
        request += "JOIN {1} ON {0}.lesson_id={1}.id "
        params.append(DataBase.Schema.lessons.name)
        if student_list is not None or student_id is not None:
            if student_list is not None:
                request += "WHERE {0}.student_id IN ({" + str(len(params)) + "}) "
                params.extend(student_list)
            else:
                request += "WHERE {0}.student_id={" + str(len(params)) + "} "
                params.append(student_id)
        request, params = self.set_request_params(request, params, group_id, "{1}.group_id={" + str(len(params)) + "} ",
                                                  2)
        request, params = self.set_request_params(request, params, professor_id,
                                                  "{1}.professor_id={" + str(len(params)) + "} ",
                                                  2)
        request, params = self.set_request_params(request, params, discipline_id,
                                                  "{1}.discipline_id={" + str(len(params)) + "} ",
                                                  2)
        request, params = self.set_request_params(request, params, synch, "{0}.synch={" + str(len(params)) + "}", 2)

        return [
            {
                "student_id": str(res[0]),
                "lesson_id": str(res[1])
            } for res in self.sql_request(request, *tuple(params))]

    def get_table(self, student_id=None, professor_id=None,
                  discipline_id=None, group_id=None, user_type=None) -> List or Dict:
        if user_type is None:
            request = """
            SELECT
                {0}.date,
                CASE lessons.complete
                    WHEN 1 THEN {2}.student_id
                    WHEN 0 THEN -1
                END
            FROM {0}
            JOIN {1} ON {1}.group_id={0}.group_id
            LEFT JOIN {2} ON {2}.student_id={1}.student_id AND {0}.id={2}.lesson_id
            """
            params = [DataBase.Schema.lessons.name,
                      DataBase.Schema.students_groups.name,
                      DataBase.Schema.visitations.name]
            if student_id is not None:
                request += and_or_where(params, 3) + "{1}.student_id={" + str(len(params)) + "} "
                params.append(student_id)
            if professor_id is not None:
                request += and_or_where(params, 3) + "{0}.professor_id={" + str(len(params)) + "} "
                params.append(professor_id)
            if group_id is not None:
                request += and_or_where(params, 3) + "{0}.group_id={" + str(len(params)) + "} "
                params.append(group_id)
            if discipline_id is not None:
                request += and_or_where(params, 3) + "{0}.discipline_id={" + str(len(params)) + "} "
                params.append(discipline_id)
            request += "ORDER BY {0}.date; "
            print(self.sql_request(request, *tuple(params)))
            return [
                {
                    "student_id": "-1" if str(i[1]) == "-1" else ("1" if str(i[1]) == str(student_id) else "0")
                } for i in self.sql_request(request, *tuple(params))
            ]
        elif str(user_type) == "1":
            return {
                "lessons": [[lesson["date"], lesson["type"]] for lesson in
                            self.get_lessons(professor_id=professor_id, group_id=group_id,
                                             discipline_id=discipline_id)],
                "students": [{
                    "first_name": student["first_name"],
                    "last_name": student["last_name"],
                    "middle_name": student["middle_name"],
                    "visitations": [c["student_id"] for c in
                                    self.get_table(student_id=student["id"], discipline_id=discipline_id,
                                                   professor_id=professor_id, group_id=group_id)]
                } for student in self.get_students(group_id=group_id)
                ]
            }
        elif str(user_type) == "0":
            return {
                "lessons": [[lesson["date"], lesson["type"]] for lesson in self.get_lessons(student_id=student_id,
                                                                                            discipline_id=discipline_id,
                                                                                            group_id=(self.get_groups(
                                                                                                student_id=student_id)[
                                                                                                0]["id"])
                                                                                            )],
                "students": [{
                    "first_name": student["first_name"],
                    "last_name": student["last_name"],
                    "middle_name": student["middle_name"],
                    "visitations": [c["student_id"] for c in
                                    self.get_table(student_id=student_id, discipline_id=discipline_id,
                                                   group_id=self.get_groups(student_id=student_id)[0]["id"])]
                } for student in self.get_students(student_id=student_id)
                ]
            }
        else:
            return False

    def get_total(self, admin_id=None, user_type=None):
        if str(user_type) == "2":
            request = """
                SELECT
                    {2}.id,
                    count(distinct {4}.id, {4}.student_id)/(count({3}.id))*100 AS 'ctn',
                    {2}.name
                FROM {0}
                JOIN {1} ON {0}.id={1}.student_id
                JOIN {2} ON {1}.group_id={2}.id
                JOIN {3} ON {2}.id={3}.group_id
                LEFT JOIN {4} ON {3}.id={4}.lesson_id AND {0}.id={4}.student_id
                GROUP BY {2}.id
            """
            params = [
                DataBase.Schema.students.name,
                DataBase.Schema.students_groups.name,
                DataBase.Schema.groups.name,
                DataBase.Schema.lessons.name,
                DataBase.Schema.visitations.name]
            return [{
                "id": i[0],
                "%": float(i[1]),
                "name": str(i[2])
            } for i in self.sql_request(request, *tuple(params))]
        else:
            return []

    def get_groups_of_total(self, group_id: int, admin_id=None, user_type=None):
        """
        return total visitation of student of selected group
        :param group_id: ID of group
        :param admin_id: ID of user
        :param user_type: type of user
        """
        if str(user_type) == "2":
            request = """
            SELECT
                {0}.id,
                {0}.last_name,
                {0}.first_name,
                {0}.middle_name,
                COUNT(distinct {3}.lesson_id, {3}.student_id)/(count(distinct {2}.id))*100 as '%'
            FROM {0}
            JOIN {1} on {0}.id={1}.student_id
            JOIN {2} on {1}.group_id={2}.group_id
            LEFT JOIN {3} on {2}.id={3}.lesson_id and {0}.id={3}.student_id
            WHERE {1}.group_id={4}
            GROUP BY {0}.id
            ORDER BY '%'
            """
            params = [
                DataBase.Schema.students.name,
                DataBase.Schema.students_groups.name,
                DataBase.Schema.lessons.name,
                DataBase.Schema.visitations.name,
                group_id]

            return [{
                "id": i[0],
                "last_name": i[1],
                "first_name": i[2],
                "middle_name": i[3],
                "%": float(i[4])
            } for i in self.sql_request(request, *tuple(params))]
        return []

    def get_the_lessons_count(self, student_id: int or str, discipline_id: int or str) -> int:
        """

        :param student_id: ID of student
        :param discipline_id: ID of discipline
        :return: number of completed lessons
        """
        return self.sql_request("SELECT COUNT(DISTINCT id) FROM {0} "
                                "JOIN {1} ON {1}.group_id={0}.group_id "
                                "WHERE {1}.student_id={2} AND {0}.discipline_id={3}",
                                DataBase.Schema.lessons.name,
                                DataBase.Schema.students_groups.name,
                                student_id,
                                discipline_id)[0][0]

    def get_visited_lessons_count(self, student_id: int or str, discipline_id: int or str) -> int:
        """

        :param student_id: ID of student
        :param discipline_id: ID of discipline
        :return: number of visited lessons
        """
        return self.sql_request("SELECT COUNT(DISTINCT {0}.id) FROM {0} "
                                "JOIN {1} ON {1}.id={0}.id "
                                "JOIN {2} ON {1}.group_id={2}.group_id "
                                "WHERE {2}.student_id={3} AND {1}.discipline_id={4}",
                                DataBase.Schema.visitations.name,
                                DataBase.Schema.lessons.name,
                                DataBase.Schema.students_groups.name,
                                student_id,
                                discipline_id)[0][0]

    def get_data_for_student_table(self, student_id: int or str, group_id: int or str, discipline_id) -> dict:
        """

        :param student_id: student ID
        :param group_id: group ID
        :param discipline_id: data if disciplines
        :return: data dict
        """
        visitation = self.sql_request("SELECT DISTINCT {0}.id, {1}.discipline_id, {1}.date FROM {0} "
                                      "JOIN {1} ON {1}.id={0}.id "
                                      "WHERE {0}.student_id={2} AND {1}.group_id={3} AND {1}.discipline_id in ({4})",
                                      DataBase.Schema.visitations.name,
                                      DataBase.Schema.lessons.name,
                                      student_id,
                                      group_id,
                                      discipline_id
                                      )
        try:
            data = {
                "data": [{"col_id": visitation[i][0], "row_id": visitation[i][1]} for i in range(len(visitation))],
                "cols_head": {lesson["id"]: lesson["date"] for lesson in self.get_lessons(student_id=student_id)},
                "rows_head": self.get_disciplines(discipline_id=discipline_id)[0]["name"],
                "head":
                    {
                        "Группа": self.get_groups(group_id=group_id),
                        "Студент": self.get_student_name(student_id=student_id),
                        "Дисциплина": self.get_disciplines(discipline_id=discipline_id),
                        "Преподаватель": self.get_professors(group_id=group_id, discipline_id=discipline_id)[0]
                    }
            }
            return data
        except Exception as e:
            raise e

    def get_data_for_professor(self, discipline_id: int or str, group_id: int or str, professor_id: int or str,
                               student_list):
        """

        :param discipline_id:
        :param group_id:
        :param professor_id:
        :param student_list:
        :return:
        """
        discipline_id = int(discipline_id)
        group_id = int(group_id)
        professor_id = int(professor_id)
        data = {"students": self.get_students(group_id=group_id,
                                              student_list=student_list),
                "lessons": self.get_lessons(group_id=group_id, professor_id=professor_id, discipline_id=discipline_id),
                "data": self.get_visitations(group_id=group_id,
                                             professor_id=professor_id,
                                             discipline_id=discipline_id,
                                             student_list=student_list),
                "professor_name": self.get_professors(professor_id=professor_id)[0],
                "discipline_name": self.get_disciplines(discipline_id=discipline_id)[0]["name"],
                "group_name": self.get_groups(group_id=group_id)
                }
        return data
