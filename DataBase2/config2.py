from Parser.server import server_args


class Config:
    schemas = {'mysql': 'mysql+pymysql'}
    connection_string = f"{schemas[server_args.database_server]}://{server_args.database_login}:{server_args.database_password}@{server_args.database_host}/{server_args.database_database}?charset=utf8"
