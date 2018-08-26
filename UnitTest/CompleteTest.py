import unittest
from unittest import TestCase

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


if __name__ == "__main__":
    unittest.main()
