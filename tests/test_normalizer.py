"""Unit test suite for normalizer module."""

import unittest
from minesword.normalizer import normalize_text, tokenize


class TestNormalizer(unittest.TestCase):

    def test_persian_arabic_unification(self):
        text = "كتابهای آموزشی يزد 1234 ة أ إ آ ؤ ئ"
        normalized = normalize_text(text)
        self.assertIn("کتابهای", normalized)
        self.assertIn("یزد", normalized)
        self.assertIn("1234", normalized)
        self.assertIn("ه", normalized)
        self.assertIn("ا", normalized)

    def test_zwnj_and_diacritics(self):
        text = "مَثَلاً كِتَاب‌هَای فِعْلِی"
        normalized = normalize_text(text)
        self.assertEqual(normalized, "مثلا کتاب های فعلی")

    def test_english_case_folding(self):
        text = "Minesword Search Engine RTL/LTR"
        normalized = normalize_text(text)
        self.assertEqual(normalized, "minesword search engine rtl/ltr")

    def test_tokenization(self):
        text = "موتور جستجوی ماین‌سورد (Minesword) v1.0"
        tokens = tokenize(text)
        self.assertIn("موتور", tokens)
        self.assertIn("جستجوی", tokens)
        self.assertIn("ماین", tokens)
        self.assertIn("سورد", tokens)
        self.assertIn("minesword", tokens)


if __name__ == "__main__":
    unittest.main()
