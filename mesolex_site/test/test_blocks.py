from django.core.exceptions import ValidationError
from django.test import TestCase

from mesolex_site.blocks import LanguageLinkBlock
from mesolex_site.models import LanguageHomePage


class LanguageLinkBlockTestCase(TestCase):
    def test_rejects_two_empty_fields(self):
        with self.assertRaises(ValidationError):
            LanguageLinkBlock().clean({
                'name': '',
                'language_page': None,
                'external_url': '',
            })

    def test_rejects_two_filled_fields(self):
        with self.assertRaises(ValidationError):
            LanguageLinkBlock().clean({
                'name': '',
                'language_page': LanguageHomePage(),
                'external_url': 'http://www.example.com',
            })

    def test_rejects_url_and_empty_name(self):
        with self.assertRaises(ValidationError):
            LanguageLinkBlock().clean({
                'name': '',
                'language_page': None,
                'external_url': 'http://www.example.com',
            })

    def test_accepts_page_and_no_url(self):
        LanguageLinkBlock().clean({
            'name': '',
            'language_page': LanguageHomePage(),
            'external_url': '',
        })

    def test_accepts_url_and_no_page(self):
        LanguageLinkBlock().clean({
            'name': 'External link',
            'language_page': None,
            'external_url': 'http://www.example.com',
        })
