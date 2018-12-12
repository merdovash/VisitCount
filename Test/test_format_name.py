from unittest import TestCase

from DataBase2 import Professor
from DataBase2.Types import format_name


class TestFormat_name(TestCase):
    def test_format_name_dict(self):
        self.assertEqual('Иванов Иван Иванович',
                         format_name({'last_name': 'Иванов', 'first_name': 'Иван',
                                      'middle_name': 'Иванович'}))

    def test_student(self):
        from DataBase2 import Student
        self.assertEqual('Иванов Иван Иванович',
                         format_name(Student(**{'last_name': 'Иванов', 'first_name': 'Иван',
                                                'middle_name': 'Иванович', 'card_id': ''})))

    def test_professor(self):
        from DataBase2 import Professor
        self.assertEqual('Иванов Иван Иванович',
                         format_name(Professor(**{'last_name': 'Иванов', 'first_name': 'Иван',
                                                  'middle_name': 'Иванович', 'card_id': ''})))

    def test_empty_middle_name_professor(self):
        self.assertEqual('Иванов Иван',
                         format_name(Professor(**{'last_name': 'Иванов', 'first_name': 'Иван',
                                                  'middle_name': '', 'card_id': ''})))

    def test_empty_middle_name_dict(self):
        self.assertEqual('Иванов Иван',
                         format_name({'last_name': 'Иванов', 'first_name': 'Иван',
                                      'middle_name': ''}))

    def test_no_middle_name_dict(self):
        self.assertEqual('Иванов Иван',
                         format_name({'last_name': 'Иванов', 'first_name': 'Иван'}))

    def test_custom_object(self):
        class custom_class:
            last_name = 'Иванов'
            first_name = 'Иван'
            middle_name = 'Иванович'

        self.assertEqual('Иванов Иван Иванович',
                         format_name(custom_class()))

    def test_custom_object_with_no_middle_name(self):
        class custom_class:
            last_name = 'Иванов'
            first_name = 'Иван'

        self.assertEqual('Иванов Иван',
                         format_name(custom_class()))
