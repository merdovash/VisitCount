from unittest import TestCase

from Domain.Validation import Values


class TestValidateGet(TestCase):
    def test_table_name_student(self):
        from DataBase2 import Student
        student = Student()

        self.assertEqual('Student', Values.Get.table_name(student))

    def test_table_name_declarative_meta(self):
        from DataBase2 import Student
        student = Student

        self.assertEqual('Student', Values.Get.table_name(student))

    def test_table_name_int(self):
        f = 14

        with self.assertRaises(NotImplementedError):
            Values.Get.table_name(f)

    def test_table_name_type_int(self):
        f = type(42)

        with self.assertRaises(NotImplementedError):
            Values.Get.table_name(f)

    def test_table_name_by_name(self):
        f = 'Student'

        self.assertEqual(Values.Get.table_name(f), 'Student')
