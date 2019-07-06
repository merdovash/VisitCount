from Parser import Args


class Config:
    schemas = {'mysql': 'mysql+pymysql'}
    connection_string = f"{schemas[Args().database_server]}://{Args().database_login}:{Args().database_password}@{Args().database_host}/{Args().database_database}?charset=utf8"
