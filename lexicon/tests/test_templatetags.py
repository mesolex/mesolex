from django.test import TestCase

from lexicon.templatetags import lexeme_tags


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
            lexeme_tags.link_vnawa(test_text),
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
            lexeme_tags.link_vnawa(test_text),
        )

        self.assertEqual(
            test_text_2,
            lexeme_tags.link_vnawa(test_text_2),
        )
