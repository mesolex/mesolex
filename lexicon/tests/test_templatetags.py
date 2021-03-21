from unittest.mock import patch

from django.test import TestCase

from lexicon.templatetags import lexeme_tags

DUMMY_DATASET_CONFIG = {
    'foo': {
        'part_of_speech': {
            'bar': 'baz',
        },
        'inflectional_type': {
            'qux': 'norf',
        },
    },
}


class LinkVnawaTestCase(TestCase):
    def test_adds_vnawa_links(self):
        test_text = """
        Foo bar <vnawa>baz</vnawa>
        """

        expected_text = """
        Foo bar <a href="/search/?form-TOTAL_FORMS=1&form-INITIAL_FORMS=0&form-MIN_NUM_FORMS=0&form-MAX_NUM_FORMS=1000&form-0-query_string=baz&form-0-operator=and&form-0-filter_on=lemma&form-0-filter=exactly_equals" class="vnawa">baz</a>
        """

        self.assertEqual(
            expected_text,
            lexeme_tags.link_vnawa(test_text, '/search/'),
        )

    def test_ignores_unclosed_tags(self):
        test_text = """
        Foo bar <vnawa>baz
        """

        test_text_2 = """
        Foo bar baz</vnawa>
        """

        self.assertEqual(
            test_text,
            lexeme_tags.link_vnawa(test_text, '/search/'),
        )

        self.assertEqual(
            test_text_2,
            lexeme_tags.link_vnawa(test_text_2, '/search/'),
        )


@patch('lexicon.templatetags.lexeme_tags.DATASET_CATEGORIES_LOOKUPS', new=DUMMY_DATASET_CONFIG)
class LinkPartOfSpeechTestCase(TestCase):
    def test_gets_human_readable_value_where_present(self):
        input = 'bar'
        expected = (
            '<a href="/search/?form-TOTAL_FORMS=1&'
            'form-INITIAL_FORMS=0&form-MIN_NUM_FORMS=0&form-MAX_NUM_FORMS=1000&'
            'form-0-query_string=bar&form-0-operator=and&'
            'form-0-filter_on=part_of_speech&form-0-filter=exactly_equals" '
            'class="pos">baz</a>'
        )
        self.assertEqual(
            expected,
            lexeme_tags.link_part_of_speech(input, '/search/', language='foo'),
        )

    def test_returns_input_where_not_present(self):
        input = 'foo'
        expected = (
            '<a href="/search/?form-TOTAL_FORMS=1&'
            'form-INITIAL_FORMS=0&form-MIN_NUM_FORMS=0&form-MAX_NUM_FORMS=1000&'
            'form-0-query_string=foo&form-0-operator=and&'
            'form-0-filter_on=part_of_speech&form-0-filter=exactly_equals" '
            'class="pos">foo</a>'
        )
        self.assertEqual(
            expected,
            lexeme_tags.link_part_of_speech(input, '/search/', language='foo'),
        )


@patch('lexicon.templatetags.lexeme_tags.DATASET_CATEGORIES_LOOKUPS', new=DUMMY_DATASET_CONFIG)
class LinkInflectionalTypeTestCase(TestCase):
    def test_gets_human_readable_value_where_present(self):
        input = 'qux'
        expected = (
            '<a href="/search/?form-TOTAL_FORMS=1&'
            'form-INITIAL_FORMS=0&form-MIN_NUM_FORMS=0&form-MAX_NUM_FORMS=1000&'
            'form-0-query_string=qux&form-0-operator=and&'
            'form-0-filter_on=inflectional_type&form-0-filter=exactly_equals" '
            'class="it">norf</a>'
        )
        self.assertEqual(
            expected,
            lexeme_tags.link_inflectional_type(input, '/search/', language='foo'),
        )

    def test_returns_input_where_not_present(self):
        input = 'foo'
        expected = (
            '<a href="/search/?form-TOTAL_FORMS=1&'
            'form-INITIAL_FORMS=0&form-MIN_NUM_FORMS=0&form-MAX_NUM_FORMS=1000&'
            'form-0-query_string=foo&form-0-operator=and&'
            'form-0-filter_on=inflectional_type&form-0-filter=exactly_equals" '
            'class="it">foo</a>'
        )
        self.assertEqual(
            expected,
            lexeme_tags.link_inflectional_type(input, '/search/', language='foo'),
        )
