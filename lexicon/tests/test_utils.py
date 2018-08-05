from django.test import TestCase

from lexicon import utils


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
