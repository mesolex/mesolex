from django.test import TestCase

from lexicon.transformations.nahuat_orthography import nahuat_orthography


class OrthographyTransformTestCase(TestCase):
    def test_respects_w_contexts(self):
        """
        The consonant 'kw' should not be subject to
        the transformations applied to 'w'.
        """
        in_string = 'kwekwawaw'
        out_string = '(kwe|cue)(kwa|qua|cua)(w|v|hu|u)a(w|v|uh|u)'
        self.assertEqual(
            out_string,
            nahuat_orthography._original_fn(in_string),
        )
    
    def test_respects_s_contexts(self):
        """
        The consonant 'ts' should not be subject to
        the transformations applied to 's'.
        """
        in_string = 'sitsesesa'
        out_string = '(si|ci)(ts|tz)e(se|ce)(sa|za|ça)'
        self.assertEqual(
            out_string,
            nahuat_orthography._original_fn(in_string),
        )
    
    def test_handles_multichar_consonants(self):
        """
        Multi-character consonants are handled correctly.
        """
        in_string = 'kwatzcuiuh'
        out_string = '(kwa|qua|cua)(ts|tz)(ku|cu|que)i(w|v|uh|u)'
        self.assertEqual(
            out_string,
            nahuat_orthography._original_fn(in_string),
        )