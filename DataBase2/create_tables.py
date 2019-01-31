def create_all_tables():
    import DataBase2
    from DataBase2 import Base, engine

    Base.metadata.create_all(engine)


if __name__ == '__main__':
    create_all_tables()
