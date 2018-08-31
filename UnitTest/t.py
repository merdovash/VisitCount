from DataBase.ServerDataBase import DataBaseWorker

if __name__ == '__main__':
    db = DataBaseWorker()
    data = {
        'visitations': [
            {'student_id': 2, 'lesson_id': 3}
        ],
        'students': [
            {'card_id': '423432', 'id': 3},
            {'last_name': 'УПЯЧКА', 'id': 4}
        ]
    }
    db.set_updates(data=data, professor_id=1)
    print(db.to_dict(db.sql_request("SELECT * from updates"), 'updates'))
    print(db.get_updates(2))
