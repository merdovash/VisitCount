from unittest import TestCase

from Domain.Validation.Values import Validate


class TestValidate(TestCase):
    def test_card_id_int(self):
        self.assertTrue(Validate.card_id(123456))

    def test_card_id_str(self):
        self.assertFalse(Validate.card_id('fgdhfjg'))

    def test_card_id_str_numeric(self):
        self.assertTrue(Validate.card_id('134567'))

    def test_card_object(self):
        self.assertFalse(Validate.card_id(object()))

    def test_card_id_str_of_number_and_letter(self):
        self.assertFalse(Validate.card_id('1212435354g'))
