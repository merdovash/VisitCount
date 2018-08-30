import unittest
from unittest import TestCase

from DataBase.Authentication import Authentication
from DataBase.ServerDataBase import DataBaseWorker
from DataBase.Types import format_name, AtrDict


class TypesTest(TestCase):
    def test_names(self):
        user = {'last_name': 'Смирнов', 'first_name': 'Иван', 'middle_name': 'Иванович'}
        self.assertEqual('Смирнов И.И.', format_name(user))

    def test_names_with_empty_middle_name(self):
        user = {'last_name': 'Смирнов', 'first_name': 'Иван', 'middle_name': ''}
        self.assertEqual('Смирнов И.', format_name(user))


class AtrDictTest(TestCase):
    def test_AtrDict(self):
        user = {'last_name': 'Смирнов', 'first_name': 'Иван', 'middle_name': 'Иванович'}
        atr_dict = AtrDict(user)
        self.assertEqual('Смирнов', atr_dict.last_name)

    def test_AtrDict_set_error(self):
        def set():
            atr_dict.a = 7

        user = {'last_name': 'Смирнов', 'first_name': 'Иван', 'middle_name': 'Иванович'}
        atr_dict = AtrDict(user)
        self.assertRaises(AttributeError, set())


class AuthenticationTest(TestCase):
    db = DataBaseWorker()

    def test_authentication_normal(self):
        auth = Authentication(db=self.db, login='VAE', password='123456')
        self.assertEqual(Authentication.Status.Complete, auth.status)

    def test_authentication_kwargs(self):
        kwargs = {
            'login': 'VAE',
            'password': '123456'
        }
        auth = Authentication(db=self.db, **kwargs)
        self.assertEqual(Authentication.Status.Complete, auth.status)

    def test_wrong_kwargs(self):
        kwargs = {
            'login': 'wrong_password',
            'password': 'wrong_login'
        }
        auth = Authentication(db=self.db, **kwargs)
        self.assertEqual(Authentication.Status.Fail, auth.status)


if __name__ == "__main__":
    unittest.main()
