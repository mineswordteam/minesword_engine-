import unittest
from minesword.normalizer import normalize_text, tokenize, normalize_digits, expand_query_synonyms


class TestNormalizerExtended(unittest.TestCase):

    def test_persian_arabic_chars(self):
        self.assertEqual(normalize_text("كتابي و هدى"), "کتابی و هدی")

    def test_digits_normalization(self):
        self.assertEqual(normalize_digits("۱۲۳۴۵۶۷۸۹۰", to_english=True), "1234567890")
        self.assertEqual(normalize_digits("123", to_english=False), "۱۲۳")

    def test_zwnj_and_diacritics(self):
        self.assertEqual(normalize_text("تَسْت\u200cکنید"), "تست کنید")

    def test_synonym_expansions(self):
        exp = expand_query_synonyms("دانلود بازی کالاف دیوتی")
        self.assertTrue(any("call of duty" in e for e in exp))


if __name__ == '__main__':
    unittest.main()
