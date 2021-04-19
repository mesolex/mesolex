from django.test import TestCase

from lexicon.transformations.juxt1235 import neutralize_glottal_stop
from lexicon.transformations.nahuat_orthography import nahuat_orthography


class NeutralizeGlottalStopTestCase(TestCase):
    def test_returns_vowels_with_optional_glottal_stops(self):
        in_string = "ae'IO'U"
        form_data = {'neutralize_glottal_stop': True}
        expected_output = "a\\'?e\\'?I\\'?O\\'?U\\'?"
        (new_form_action, affixed_qstr) = neutralize_glottal_stop('contains', '', in_string, form_data)
        self.assertEqual('__iregex', new_form_action)
        self.assertEqual(expected_output, affixed_qstr)

    def test_adds_boundaries_correctly(self):
        in_string = "tu'un"
        form_data = {'neutralize_glottal_stop': True}

        (_, prefixed_qst) = neutralize_glottal_stop('begins_with', '', in_string, form_data)
        self.assertEqual("^tu\\'?u\\'?n", prefixed_qst)

        (_, suffixed_qst) = neutralize_glottal_stop('ends_with', '', in_string, form_data)
        self.assertEqual("tu\\'?u\\'?n$", suffixed_qst)

        (_, circumfixed_qst) = neutralize_glottal_stop('exactly_equals', '', in_string, form_data)
        self.assertEqual("^tu\\'?u\\'?n$", circumfixed_qst)

        (_, unaffixed_qst) = neutralize_glottal_stop('contains', '', in_string, form_data)
        self.assertEqual("tu\\'?u\\'?n", unaffixed_qst)

    def test_ignores_if_not_neutralize_glottal_stop(self):
        in_string = "tu'un"
        form_data = {'neutralize_glottal_stop': False}
        (form_action, prefixed_qstr) = neutralize_glottal_stop('begins_with', '__istartswith', in_string, form_data)
        self.assertEqual('__istartswith', form_action)
        self.assertEqual("tu'un", prefixed_qstr)
