from django.test import TestCase

from mesolex import utils


class ContainsWordToRegexTestCase(TestCase):
    def test_encloses_query_string_in_delimiters(self):
        input = 'foo:bar'
        expected_output = '(?:^|\s|\.){query_string}(?:$|\s|\.)'.format(
            query_string=input,
        )
        (new_form_action, new_qstring) = utils.contains_word_to_regex(
            'contains_word', '', input, None
        )
        self.assertEqual('__iregex', new_form_action)
        self.assertEqual(expected_output, new_qstring)

    def test_ignores_everything_other_than_contains_word(self):
        input = 'foo:bar'
        (new_form_action, new_qstring) = utils.contains_word_to_regex(
            'begins_with', '__istartswith', input, None
        )
        self.assertEqual('__istartswith', new_form_action)
        self.assertEqual(input, new_qstring)


class ToVLNTestCase(TestCase):
    def test_returns_vowels_with_optional_length_marks(self):
        input = 'ae:IO:U'
        form_data = {'vln': True}
        expected_output = 'a:?e:?I:?O:?U:?'
        (new_form_action, affixed_qstr) = utils.to_vln('contains', '', input, form_data)
        self.assertEqual('__iregex', new_form_action)
        self.assertEqual(expected_output, affixed_qstr)

    def test_adds_boundaries_correctly(self):
        input = 'tani'
        form_data = {'vln': True}

        (_, prefixed_qst) = utils.to_vln('begins_with', '', input, form_data)
        self.assertEqual('^ta:?ni:?', prefixed_qst)

        (_, suffixed_qst) = utils.to_vln('ends_with', '', input, form_data)
        self.assertEqual('ta:?ni:?$', suffixed_qst)

        (_, circumfixed_qst) = utils.to_vln('exactly_equals', '', input, form_data)
        self.assertEqual('^ta:?ni:?$', circumfixed_qst)

        (_, unaffixed_qst) = utils.to_vln('contains', '', input, form_data)
        self.assertEqual('ta:?ni:?', unaffixed_qst)

        (_, unchanged_qst) = utils.to_vln('regex', '', input, form_data)
        self.assertEqual(unchanged_qst, input)

    def test_ignores_if_not_vln(self):
        input = 'tani'
        form_data = {'vln': False}
        (form_action, prefixed_qst) = utils.to_vln('begins_with', '__istartswith', input, form_data)
        self.assertEqual('__istartswith', form_action)
        self.assertEqual('tani', prefixed_qst)
