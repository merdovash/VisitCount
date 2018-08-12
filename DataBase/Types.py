from config2 import DataBaseConfig


def to_student(data):
    if type(data) is list:
        return [to_student(i) for i in data]
    else:
        return {
            "id": data[0],
            "last_name": data[1],
            "first_name": data[2],
            "middle_name": data[3],
            "card_id": data[4]
        }


def to_professor(data):
    if type(data) is list:
        return [to_student(i) for i in data]
    else:
        return {
            "id": data[0],
            "last_name": data[1],
            "first_name": data[2],
            "middle_name": data[3],
            "card_id": data[4]
        }


def to_parent(data):
    if type(data) is list:
        return [to_student(i) for i in data]
    else:
        return {
            "id": data[0],
            "last_name": data[1],
            "first_name": data[2],
            "middle_name": data[3]
        }


def to_lesson(data):
    if type(data) is list:
        return [to_student(i) for i in data]
    else:
        return {
            "id": data[0],
            "professor_id": data[1],
            "group_id": data[2],
            "discipline_id": data[3],
            "date": data[4],
            "room_id": data[5],
            "completed": data[6]
        }


def to_dict(table, data, config: DataBaseConfig = None):
    if (config is None and table == "students") or (config is not None and table == config.students):
        return to_student(data)
