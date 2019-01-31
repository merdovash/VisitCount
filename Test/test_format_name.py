from unittest import TestCase

from DataBase2 import Professor, Student
from Domain.Exception.Constraint import ConstraintDictNameException, ConstraintNotEmptyException
from Domain.functools.Format import format_name, Case


class TestFormatName(TestCase):
    def test_format_name_dict(self):
        self.assertEqual('Иванов Иван Иванович',
                         format_name({'last_name': 'Иванов', 'first_name': 'Иван',
                                      'middle_name': 'Иванович'}))

    def test_student(self):
        self.assertEqual('Иванов Иван Иванович',
                         format_name(Student(**{'last_name': 'Иванов', 'first_name': 'Иван',
                                                'middle_name': 'Иванович', 'card_id': ''})))

    def test_professor(self):
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
        class CustomClass:
            last_name = 'Иванов'
            first_name = 'Иван'
            middle_name = 'Иванович'

        self.assertEqual('Иванов Иван Иванович',
                         format_name(CustomClass()))

    def test_custom_object_with_no_middle_name(self):
        class CustomClass:
            last_name = 'Иванов'
            first_name = 'Иван'

        self.assertEqual('Иванов Иван',
                         format_name(CustomClass()))

    def test_lower_case_dict(self):
        self.assertEqual('Иванов Иван',
                         format_name({'last_name': 'иванов', 'first_name': 'иван'}))


class TestFormatNameWithCase(TestCase):
    def test_datv_case_student(self):
        self.assertEqual('Иванову Ивану Ивановичу',
                         format_name(Student(**{'last_name': 'Иванов',
                                                'first_name': 'Иван',
                                                'middle_name': 'Иванович',
                                                'card_id': ''}),
                                     case=Case.datv))

    def test_datv_case_student_without_middle_name(self):
        self.assertEqual('Иванову Ивану',
                         format_name(Student(**{'last_name': 'Иванов',
                                                'first_name': 'Иван',
                                                'middle_name': '',
                                                'card_id': ''}),
                                     case=Case.datv))


class TestFormatNameException(TestCase):
    def test_no_first_name(self):
        with self.assertRaises(ConstraintDictNameException):
            format_name({'last_name': 'Иванов',
                         'middle_name': 'Иванович',
                         'card_id': ''})

    def test_empty_first_name(self):
        with self.assertRaises(ConstraintNotEmptyException):
            format_name({'last_name': 'Иванов',
                         'first_name': '',
                         'middle_name': 'Иванович',
                         'card_id': ''})

    def test_empty_student_first_name(self):
        with self.assertRaises(ConstraintNotEmptyException):
            format_name(Student(**{
                'last_name': 'Иванов',
                'first_name': '',
                'middle_name': '',
                'card_id': ''
            }))
