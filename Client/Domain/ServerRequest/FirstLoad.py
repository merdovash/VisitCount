def FirstLoad(program, auth, login, password, on_finish):
    from Modules.FirstLoad.ClientSide import FirstLoad as _first_load

    _first_load(program=program, auth=auth, login=login, password=password, on_finish=on_finish).start()
