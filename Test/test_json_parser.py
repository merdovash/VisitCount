from unittest import TestCase

from DataBase2 import Visitation
from Parser.JsonParser import JsonParser


class TestJSONParser(TestCase):
    def test_visitation(self):
        self.assertEqual(
            {'_created': None, '_deleted': None, '_is_deleted': None, '_updated': None, 'id': 1, 'lesson': None,
             'lesson_id': 3, 'student': None, 'student_id': 6},
            JsonParser.read(JsonParser.dump(Visitation(id=1, lesson_id=3, student_id=6)))
            )

    def test_visitation_simple(self):
        visit = Visitation(id=6, lesson_id=4, student_id=12)
        self.assertEqual(visit._dict(), JsonParser.read(JsonParser.dump(visit)))


if __name__ == '__main__':
    pass
