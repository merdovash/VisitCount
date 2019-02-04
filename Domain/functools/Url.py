def to_standart_http(my_url):
    """
    Приводит строку Url к стандартному виду hhtp://{site_name}.{domain}
    :param my_url:
    """
    from urllib.parse import urlparse, ParseResult

    p = urlparse(my_url, 'http')
    netloc = p.netloc or p.path
    path = p.path if p.netloc else ''
    if netloc.startswith('www.'):
        netloc = netloc[4:]

    p = ParseResult('http', netloc, path, *p[3:])
    return p.geturl()
