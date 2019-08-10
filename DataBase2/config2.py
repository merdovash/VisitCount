from Parser import Args


class Config:
    schemas = {'mysql': 'mysql+pymysql', 'postgres': 'postgresql+psycopg2'}
    connection_string = f"{schemas[Args().database_server]}://{Args().database_login}{(':'+Args().database_password if Args().database_password is not None else '')}@{Args().database_host}/{Args().database_database}{'?charset=utf8' if Args().database_server == 'mysql' else ''}"
