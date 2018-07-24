from django.test import TestCase

from .data.lexicalentry import TEST_DATA
from lexicon import utils


class GetListSafeTestCase(TestCase):
    def test_returns_empty_list_if_key_not_found(self):
        """
        If the key is not found, an empty list (and not None, etc)
        should be returned.
        """
        should_be_empty_list = utils.get_list_safe(
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
        should_be_one_item_list = utils.get_list_safe(
            TEST_DATA['data'],
            'glosa',
        )
        self.assertTrue(isinstance(should_be_one_item_list, list))
        self.assertEqual(1, len(should_be_one_item_list))

    def test_returns_all_items_if_list(self):
        """
        If a list value is found at the key, it should be returned.
        """
        should_be_two_item_list = utils.get_list_safe(
            TEST_DATA['data'],
            'sigGroup',
        )
        self.assertTrue(isinstance(should_be_two_item_list, list))
        self.assertEqual(2, len(should_be_two_item_list))


class ToVLNTestCase(TestCase):
    def test_returns_vowels_with_optional_length_marks(self):
        input = 'ae:IO:U'
        expected_output = 'a:?e:?I:?O:?U:?'
        (_, affixed_qstr) = utils.to_vln('contains', input)
        self.assertEqual(expected_output, affixed_qstr)

    def test_adds_boundaries_correctly(self):
        input = 'tani'

        (_, prefixed_qst) = utils.to_vln('begins_with', input)
        self.assertEqual('^ta:?ni:?', prefixed_qst)

        (_, suffixed_qst) = utils.to_vln('ends_with', input)
        self.assertEqual('ta:?ni:?$', suffixed_qst)

        (_, circumfixed_qst) = utils.to_vln('exactly_equals', input)
        self.assertEqual('^ta:?ni:?$', circumfixed_qst)

        (_, unaffixed_qst) = utils.to_vln('contains', input)
        self.assertEqual('ta:?ni:?', unaffixed_qst)

        (_, unchanged_qst) = utils.to_vln('regex', input)
        self.assertEqual(unchanged_qst, input)
