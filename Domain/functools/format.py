def js_format(js: str, **kwargs):
    for key, val in kwargs.items():
        js = js.replace('{' + key + '}', str(val))

    return js