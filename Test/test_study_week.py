from datetime import datetime
from unittest import TestCase

from Domain.Date import study_week


class TestStudy_week(TestCase):
    def test_1st_sem_date(self):
        self.assertEqual(1, study_week(datetime(2018, 2, 5)))

    def test_2nd_sem_date(self):
        self.assertEqual(1, study_week(datetime(2018, 9, 1)))

    def test_30_august_date(self):
        self.assertEqual(30, study_week(datetime(2018, 8, 30)))

    def test_4_february_2018(self):
        self.assertEqual(23, study_week(datetime(2018, 2, 3)))

    def test_1st_sem_start_2019(self):
        self.assertEqual(1, study_week(datetime(2019, 2, 4)))
