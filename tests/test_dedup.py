import unittest
from minesword.dedup import compute_content_hash, is_near_duplicate


class TestDedup(unittest.TestCase):

    def test_exact_hash(self):
        h1 = compute_content_hash("تست متن آنلاین")
        h2 = compute_content_hash("تست متن آنلاین")
        self.assertEqual(h1, h2)

    def test_near_duplicate(self):
        t1 = "دانلود جدیدترین بازی کالاف دیوتی همراه با لایسنس معتبر برای سیستم"
        t2 = "دانلود جدیدترین بازی کالاف دیوتی همراه با لایسنس معتبر کامپیوتر"
        self.assertTrue(is_near_duplicate(t1, t2, threshold=0.6))


if __name__ == '__main__':
    unittest.main()
