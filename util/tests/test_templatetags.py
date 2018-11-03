from django.test import TestCase, RequestFactory

from util.templatetags import util_tags


class TestBuildAbsoluteUri(TestCase):

    def setUp(self):
        super().setUp()
        self.context = {
            'request': RequestFactory().get("/"),
        }

    def test_internal_url(self):
        """
        Tag should add domain to an internal URL.
        """
        url = "/test/"
        result = util_tags.build_absolute_uri(self.context, url)
        self.assertEqual(result, "http://testserver" + url)

    def test_external_url(self):
        """
        Tag should not modify an external URL.
        """
        url = "https://example.com"
        result = util_tags.build_absolute_uri(self.context, url)
        self.assertEqual(result, url)
