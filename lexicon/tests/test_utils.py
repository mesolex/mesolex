from django.test import TestCase

from .data.lexicalentry import TEST_DATA
from lexicon import utils


class PluralDataTestCase(TestCase):
    def test_returns_empty_list_if_key_not_found(self):
        """
        If the key is not found, an empty list (and not None, etc)
        should be returned.
        """
        should_be_empty_list = utils.plural_data(
            TEST_DATA['data'],
            'not found',
        )
        self.assertTrue(isinstance(should_be_empty_list, list))
        self.assertEqual(0, len(should_be_empty_list))

    def test_returns_one_item_list_if_not_list(self):
        """
        If the value at the key is not a list (e.g. it's a string),
        a single-item list should be returned.
        """
        should_be_one_item_list = utils.plural_data(
            TEST_DATA['data'],
            'glosa',
        )
        self.assertTrue(isinstance(should_be_one_item_list, list))
        self.assertEqual(1, len(should_be_one_item_list))

    def test_returns_all_items_if_list(self):
        """
        If a list value is found at the key, it should be returned.
        """
        should_be_two_item_list = utils.plural_data(
            TEST_DATA['data'],
            'sigGroup',
        )
        self.assertTrue(isinstance(should_be_two_item_list, list))
        self.assertEqual(2, len(should_be_two_item_list))
