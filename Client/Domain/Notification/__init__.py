from DataBase2 import session, Administration, Professor, NotificationParam


def add_contact(last_name, first_name, middle_name, email, professor: Professor):
    new_admin = Administration(last_name=last_name, first_name=first_name,
                               middle_name=middle_name, email=email)

    np = NotificationParam(professor=professor, admin=new_admin)

    session.commit()
