def without_None(*items):
    return [i for i in items if i not in (None, 'None')]
