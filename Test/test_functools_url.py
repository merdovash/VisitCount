from unittest import TestCase

from Domain.functools.Url import to_standart_http


class TestUrl(TestCase):
    def test_case_with_www(self):
        url = 'www.google.com'

        self.assertEqual('http://google.com', to_standart_http(url))

    def test_case_with_3rd_layer(self):
        url = 'my_subdomain.google.com'

        self.assertEqual('http://my_subdomain.google.com', to_standart_http(url))

    def test_case_with_ip(self):
        url = '127.0.0.1'

        self.assertEqual('http://127.0.0.1', to_standart_http(url))

    def test_case_with_http(self):
        url = 'http://some.site.ru'

        self.assertEqual('http://some.site.ru', to_standart_http(url))

    def test_case_with_https(self):
        url = 'https://some.site.ru'

        self.assertEqual('http://some.site.ru', to_standart_http(url))
