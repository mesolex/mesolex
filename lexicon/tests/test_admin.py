import csv
from os.path import dirname, join

from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase

from lexicon.admin import MediaCSVUploadForm


class MediaCSVUploadFormTest(TestCase):
    def _create_file(self, filename):
        upload_file = open(join(dirname(__file__), 'data', filename), 'rb')
        return SimpleUploadedFile(upload_file.name, upload_file.read())

    def test_rejects_csv_with_too_few_headers(self):
        post_data = {'csv_file': self._create_file('not-enough-cols.csv')}
        form = MediaCSVUploadForm({}, post_data)
        self.assertFalse(form.is_valid())

    def test_rejects_csv_with_wrong_headers(self):
        post_data = {'csv_file': self._create_file('misspelled-cols.csv')}
        form = MediaCSVUploadForm({}, post_data)
        self.assertFalse(form.is_valid())
    
    def test_accepts_csv_with_correct_headers(self):
        post_data = {'csv_file': self._create_file('some-empty-cols.csv')}
        form = MediaCSVUploadForm({}, post_data)
        self.assertTrue(form.is_valid())